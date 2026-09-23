from __future__ import annotations

import re
from typing import Any

from core.state import AgentState


def _coalesce_message_text(messages: Any) -> str:
    if not messages:
        return ""

    text_parts: list[str] = []
    for item in messages:
        if hasattr(item, "content"):
            content = getattr(item, "content")
            if isinstance(content, str):
                text_parts.append(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        text = block.get("text") or block.get("content") or ""
                    else:
                        text = str(block)
                    text_parts.append(str(text))
        elif isinstance(item, str):
            text_parts.append(item)
        elif isinstance(item, dict):
            text = item.get("content") or item.get("text") or ""
            if text:
                text_parts.append(str(text))
    return " ".join(text_parts)


def _extract_unit_id(text: str) -> str | None:
    patterns = [
        r"(?:unit|equipment|machine)[\s:_-]*([A-Za-z0-9-]{3,12})",
        r"\b(HD\d{3,5}(?:[-_ ]?\d{1,4})?)\b",
        r"\b([A-Z]{2,4}[-_ ]?\d{2,5}(?:[-_ ]?\d{1,4})?)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            candidate = match.group(1).strip().upper()
            if candidate and "B0NX" not in candidate and not re.fullmatch(r"[A-Z0-9]{4,8}", candidate):
                return candidate

    return None


def _extract_error_code(text: str) -> str | None:
    candidates = re.findall(
        r"\b(?:[A-Z]-\d{1,2}|[A-HJ-NP-Z]{1,3}\d{2,}[A-Z0-9]*|[A-Z]{2,4}\d{2,}[A-Z0-9]*)\b",
        text.upper(),
    )

    for candidate in candidates:
        cleaned = candidate.strip().upper()
        if len(cleaned) >= 4 and any(ch.isdigit() for ch in cleaned) and any(ch.isalpha() for ch in cleaned):
            if cleaned not in {"HD785", "UNIT"}:
                return cleaned

    for code in ("15B0NX", "CA144", "H-12"):
        if code in text.upper():
            return code

    return None


def _telemetry_value(state: AgentState, key: str, legacy_key: str | None = None) -> float | None:
    value = state.get(key)
    if value is None and legacy_key:
        telemetry_data = state.get("telemetry_data", {})
        value = telemetry_data.get(legacy_key) if isinstance(telemetry_data, dict) else None
    if value is None:
        telemetry_data = state.get("telemetry_data", {})
        if isinstance(telemetry_data, dict):
            value = telemetry_data.get(key)
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def triage_agent(state: AgentState) -> AgentState:
    text = _coalesce_message_text(state.get("messages", []))
    compact_text = text.upper()

    error_code = _extract_error_code(compact_text) or state.get("active_dtc") or state.get("error_code")
    unit_id = _extract_unit_id(compact_text) or state.get("unit_id")

    payload = _telemetry_value(state, "payload_ton")
    coolant = _telemetry_value(state, "engine_coolant_temp_c", "engine_water_temp")
    transmission = _telemetry_value(state, "transmission_oil_temp_c", "tc_oil_temp")
    brake_pressure = _telemetry_value(state, "brake_air_pressure_mpa", "brake_air_pressure")
    vibration = _telemetry_value(state, "vibration_rms_mms")
    filter_delta_p = _telemetry_value(state, "filter_delta_p_psi")

    critical_reasons: list[str] = []
    warning_reasons: list[str] = []

    # 1. Muatan (Kepmen ESDM 1827 / Komatsu Specs)
    if payload is not None and payload > 91:
        critical_reasons.append(f"Payload {payload:.1f} ton melebihi batas 91 ton.")

    # 2. Suhu Pendingin Mesin
    if coolant is not None and coolant > 102:
        critical_reasons.append(f"Suhu coolant {coolant:.1f}°C melebihi batas kritis 102°C.")

    # 3. Suhu Transmisi
    if transmission is not None and transmission > 100:
        critical_reasons.append(f"Suhu transmisi {transmission:.1f}°C berada di atas batas kritis 100°C.")
    elif transmission is not None and transmission > 91.6:
        warning_reasons.append(f"Suhu transmisi {transmission:.1f}°C melebihi batas peringatan 91.6°C.")

    # 4. Beda Tekanan Filter (Filter Delta P)
    if filter_delta_p is not None and filter_delta_p >= 18.0:
        critical_reasons.append(f"Beda tekanan filter transmisi {filter_delta_p:.1f} psi (indikasi filter tersumbat).")
    elif filter_delta_p is not None and filter_delta_p >= 15.0:
        warning_reasons.append(f"Beda tekanan filter {filter_delta_p:.1f} psi mendekati batas jenuh.")

    # 5. Tekanan Udara Rem
    if brake_pressure is not None and brake_pressure < 0.65:
        critical_reasons.append(f"Tekanan rem {brake_pressure:.3f} MPa di bawah batas aman 0.65 MPa.")

    # 6. Getaran Gardan (Vibration RMS)
    if vibration is not None and vibration > 4.5:
        critical_reasons.append(f"Getaran gardan {vibration:.2f} mm/s berada pada zona kritis (risiko bearing rusak).")
    elif vibration is not None and vibration > 2.8:
        warning_reasons.append(f"Getaran gardan {vibration:.2f} mm/s meningkat di atas toleransi normal.")

    priority = "CRITICAL" if critical_reasons else "WARNING" if warning_reasons else "NORMAL"
    state["triage_priority"] = priority
    state["triage_reasons"] = critical_reasons + warning_reasons
    state["active_dtc"] = error_code

    # Pertahankan telemetry_data mentah agar tidak hilang di state
    raw_telemetry = state.get("telemetry_data")
    telemetry_data = dict(raw_telemetry) if isinstance(raw_telemetry, dict) else {}

    telemetry_keywords = [
        "telemetri", "sensor", "temperature", "pressure", "vibration",
        "rpm", "load", "oil", "anomaly", "warning", "flow", "voltage", "ampere",
    ]
    field_keywords = [
        "keluhan", "lapangan", "operator", "manual", "mekanik",
        "berhenti", "bocor", "getaran", "tidak bisa", "perbaikan", "kerusakan",
    ]

    telemetry_detected = any(k in compact_text for k in telemetry_keywords)
    field_detected = any(k in compact_text for k in field_keywords)

    if telemetry_detected:
        telemetry_data["_source"] = "telemetry"
        telemetry_data["_signals"] = [k for k in telemetry_keywords if k in compact_text]
    elif field_detected:
        telemetry_data["_source"] = "field_report"
        telemetry_data["_signals"] = [k for k in field_keywords if k in compact_text]

    state["unit_id"] = unit_id
    state["error_code"] = error_code
    state["telemetry_data"] = telemetry_data
    state["is_verified"] = False
    state["retry_count"] = int(state.get("retry_count", 0))
    state["safety_alerts"] = state.get("safety_alerts", [])
    state["requires_loto"] = bool(critical_reasons or state.get("requires_loto", False))
    state["retrieved_docs"] = state.get("retrieved_docs", [])
    state["spare_parts_found"] = state.get("spare_parts_found", [])
    state["diagnostic_result"] = state.get("diagnostic_result", {})

    return state


__all__ = ["triage_agent"]