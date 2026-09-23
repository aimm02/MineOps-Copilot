from __future__ import annotations

from core.state import AgentState


def verifier_agent(state: AgentState) -> AgentState:
    diagnostic_result = state.get("diagnostic_result") or {}
    safety_alerts = state.get("safety_alerts") or []
    requires_loto = bool(state.get("requires_loto", False))
    safety_requirements = state.get("safety_requirements") or []
    human_approval_required = bool(state.get("human_approval_required", False))

    valid = bool(diagnostic_result.get("summary") or diagnostic_result.get("recommendation"))
    if requires_loto and (not safety_alerts or not safety_requirements):
        valid = False

    if not valid:
        state["is_verified"] = False
        state["retry_count"] = int(state.get("retry_count", 0)) + 1
        diagnostic_result["verification_note"] = (
            "Instruksi keselamatan atau rekomendasi diagnostik belum cukup lengkap untuk validasi final."
        )
        state["diagnostic_result"] = diagnostic_result
        return state

    has_safety_requirement = bool(state.get("requires_loto", False))
    if has_safety_requirement and (
        not any("LOTO" in alert.upper() for alert in safety_alerts)
        or not any("LOTO" in requirement.upper() for requirement in safety_requirements)
    ):
        state["is_verified"] = False
        state["retry_count"] = int(state.get("retry_count", 0)) + 1
        diagnostic_result["verification_note"] = (
            "Validasi gagal karena instruksi keselamatan penting dari safety_agent tidak dipertahankan."
        )
        state["diagnostic_result"] = diagnostic_result
        return state

    work_steps = diagnostic_result.get("work_steps") or state.get("diagnostic_steps") or []
    priority = state.get("triage_priority", "NORMAL")
    approval_status = "MENUNGGU PERSETUJUAN MANUSIA" if human_approval_required and not state.get("human_approved", False) else "DISETUJUI"
    work_order = [
        "# Perintah Kerja Pemeliharaan",
        "",
        f"- Unit: {state.get('unit_id', 'Tidak diketahui')}",
        f"- Prioritas: {priority}",
        f"- Status verifikasi: {approval_status}",
        "",
        "## Persyaratan K3",
        *[f"- {requirement}" for requirement in safety_requirements],
        "",
        "## Langkah Diagnostik",
        *[f"{step}" for step in work_steps],
        "",
        "## Suku Cadang Rekomendasi",
        *[f"- {part}" for part in (state.get("recommended_parts") or ["Belum ditentukan"])],
    ]

    state["verifier_approved"] = valid
    state["work_order_markdown"] = "\n".join(work_order)
    state["is_verified"] = valid
    state["retry_count"] = int(state.get("retry_count", 0))
    diagnostic_result["verification_note"] = "Instruksi keselamatan, hasil retrieval, dan rekomendasi perbaikan telah diaudit." if valid else "Audit verifier belum lolos."
    state["diagnostic_result"] = diagnostic_result
    return state


__all__ = ["verifier_agent"]
