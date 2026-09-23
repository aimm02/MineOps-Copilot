from __future__ import annotations

import re

from core.state import AgentState
from src.tools.sql_tools import get_spare_part_stock, get_trouble_code_info, get_unit_history
from src.tools.vector_tools import similarity_search_with_score


def _message_text(state: MiningAgentState) -> str:
    collected: list[str] = []
    for item in state.get("messages", []):
        if hasattr(item, "content"):
            content = item.content
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        value = block.get("text") or block.get("content") or ""
                        if value:
                            collected.append(str(value))
                    else:
                        collected.append(str(block))
            elif isinstance(content, str):
                collected.append(content)
        elif isinstance(item, str):
            collected.append(item)
    return " ".join(collected)


def _extract_part_numbers(text: str) -> list[str]:
    matches = re.findall(r"\b[A-Z0-9-]{4,20}\b", text.upper())
    cleaned = []
    for value in matches:
        if len(value) >= 4 and any(ch.isdigit() for ch in value):
            if value not in cleaned:
                cleaned.append(value)
    return cleaned


def diagnostic_agent(state: AgentState) -> AgentState:
    error_code = state.get("active_dtc") or state.get("error_code")
    issue_text = _message_text(state)
    query = f"{error_code or ''} {issue_text}".strip()

    manual_docs: list[str] = []
    rag_success = False
    try:
        if query:
            scored_docs = similarity_search_with_score(query, k=5)
            accepted = [
                (doc, score)
                for doc, score in scored_docs
                if getattr(doc, "page_content", None) and float(score) <= 0.65
            ]
            if not accepted and scored_docs:
                accepted = [
                    (doc, score)
                    for doc, score in scored_docs[:2]
                    if getattr(doc, "page_content", None)
                ]
            manual_docs = [doc.page_content[:500].strip() for doc, _ in accepted]
            rag_success = bool(manual_docs)
    except Exception:
        manual_docs = []

    trouble_info = get_trouble_code_info(error_code) if error_code else None
    spare_parts_found: list[dict] = []
    recommended_parts: list[str] = []

    if trouble_info:
        part_no = trouble_info.get("part_no")
        if part_no:
            stock_entry = get_spare_part_stock(str(part_no))
            if stock_entry:
                spare_parts_found.append({"part_no": part_no, "stock": stock_entry})
                recommended_parts.append(str(part_no))

    for part_no in _extract_part_numbers(issue_text):
        stock_entry = get_spare_part_stock(part_no)
        if stock_entry and all(part.get("part_no") != part_no for part in spare_parts_found):
            spare_parts_found.append({"part_no": part_no, "stock": stock_entry})
            recommended_parts.append(str(part_no))

    unit_id = state.get("unit_id")
    unit_history = []
    if unit_id:
        unit_history = get_unit_history(unit_id)

    recommendation_parts = []
    if trouble_info and trouble_info.get("description"):
        recommendation_parts.append(f"Penyebab yang paling mungkin: {trouble_info.get('description')}.")
    if manual_docs:
        recommendation_parts.append("Bandingkan kondisi mesin dengan referensi manual yang relevan untuk memastikan langkah kerja sesuai prosedur teknis.")
    if spare_parts_found:
        recommendation_parts.append("Pastikan suku cadang yang dibutuhkan tersedia sesuai stok sebelum pekerjaan perbaikan dimulai.")
    else:
        recommendation_parts.append("Cek ketersediaan suku cadang dan lakukan koordinasi pembelian atau pengadaan bila stok tidak tersedia.")
    if unit_history:
        recommendation_parts.append("Tinjau riwayat perbaikan unit untuk melihat pola kegagalan sebelumnya yang serupa.")

    diagnostic_result = {
        "summary": (
            trouble_info.get("description")
            if trouble_info and trouble_info.get("description")
            else "Analisis awal menunjukkan kemungkinan masalah pada sistem terkait kode gangguan dan kondisi operasional unit."
        ),
        "manual_refs": manual_docs,
        "spare_parts_found": spare_parts_found,
        "unit_history": unit_history,
        "recommendation": " ".join(recommendation_parts),
        "work_steps": [
            "1. Verifikasi unit, kode gangguan, dan sumber sinyal telemetri atau keluhan lapangan.",
            "2. Lakukan langkah pengamanan K3 dan LOTO sesuai kebutuhan sistem yang terlibat.",
            "3. Bandingkan kondisi aktual dengan referensi manual resmi dan catat parameter operasional yang relevan.",
            "4. Cek ketersediaan suku cadang dan siapkan alat serta material yang dibutuhkan.",
            "5. Lakukan perbaikan sesuai prosedur teknis lalu validasi hasil setelah unit beroperasi kembali.",
        ],
    }

    state["retrieved_docs"] = manual_docs
    state["spare_parts_found"] = spare_parts_found
    state["diagnostic_result"] = diagnostic_result
    state["rag_retrieval_success"] = rag_success
    state["diagnostic_steps"] = diagnostic_result["work_steps"]
    state["recommended_parts"] = list(dict.fromkeys(recommended_parts))

    return state


__all__ = ["diagnostic_agent"]
