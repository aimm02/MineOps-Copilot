from __future__ import annotations

from core.state import AgentState


def _contains_any(text: str, keywords: list[str]) -> bool:
    normalized = text.lower()
    return any(keyword.lower() in normalized for keyword in keywords)


def safety_agent(state: AgentState) -> AgentState:
    text = " ".join(
        getattr(message, "content", str(message)) if hasattr(message, "content") else str(message)
        for message in state.get("messages", [])
    )

    alerts: list[str] = []
    requirements: list[str] = []
    requires_loto = False

    high_pressure_keywords = ["hidrolik", "hydraulic", "bertekanan tinggi", "high pressure"]
    dump_keywords = ["bak dump", "dump body", "dump truck", "hoist", "angkat bak"]
    brake_keywords = ["rem", "brake", "brakes"]
    electrical_keywords = ["listrik", "electrical", "kelistrikan", "motor", "panel", "relay"]

    priority = state.get("triage_priority", "NORMAL")
    telemetry_risk = priority in {"WARNING", "CRITICAL"}
    if telemetry_risk or _contains_any(text, high_pressure_keywords + dump_keywords + brake_keywords + electrical_keywords):
        requires_loto = True
        requirements.append("Terapkan LOTO dan verifikasi zero-energy state sebelum inspeksi atau perbaikan.")
        alerts.append("Wajib LOTO sesuai Kepmen ESDM 1827/2018 sebelum pekerjaan dimulai.")

    if _contains_any(text, high_pressure_keywords):
        requirements.append("Lakukan depresurisasi fluida hidrolik dan pastikan tekanan tersisa nol.")
        alerts.append("Pastikan semua katup dan tekanan hidrolik dibebaskan sesuai prosedur Komatsu HD785 sebelum membuka jalur hidrolik.")

    if _contains_any(text, dump_keywords):
        requirements.append("Pasang pin pengaman bak dump body sebelum bekerja di bawah atau sekitar bak.")
        alerts.append("Jaga posisi bak dump aman dan kunci perangkat pengangkat sebelum perbaikan mekanis atau elektro-hidrolik.")

    if _contains_any(text, brake_keywords):
        requirements.append("Depresurisasi sistem pneumatik/rem dan cegah pelepasan energi tersimpan.")
        alerts.append("Pastikan unit dalam kondisi aman dan rem tidak diberi beban/tekanan saat dilakukan inspeksi dan penggantian komponen.")

    if _contains_any(text, electrical_keywords):
        requirements.append("Putuskan sumber listrik, kunci isolator, dan verifikasi tidak ada tegangan.")
        alerts.append("Matikan sumber tenaga utama dan lepaskan tegangan sebelum pekerjaan pada panel, kabel, dan komponen kelistrikan.")

    if not alerts:
        alerts.append("Tidak ada indikasi pekerjaan K3 kritis yang memerlukan LOTO berdasarkan input saat ini.")

    if not requirements:
        requirements.append("Lakukan inspeksi awal dan pastikan area kerja aman sebelum operasi.")

    state["requires_loto"] = requires_loto
    state["safety_alerts"] = alerts
    state["safety_requirements"] = list(dict.fromkeys(requirements))
    state["human_approval_required"] = priority in {"WARNING", "CRITICAL"}

    return state


__all__ = ["safety_agent"]
