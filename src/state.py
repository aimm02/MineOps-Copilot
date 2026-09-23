from __future__ import annotations

from typing import Annotated, Any, NotRequired, TypedDict

from langgraph.graph.message import add_messages


class MiningAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    unit_id: NotRequired[str | None]
    error_code: NotRequired[str | None]
    telemetry_data: NotRequired[dict[str, Any]]
    safety_alerts: NotRequired[list[str]]
    requires_loto: NotRequired[bool]
    retrieved_docs: NotRequired[list[str]]
    spare_parts_found: NotRequired[list[dict[str, Any]]]
    diagnostic_result: NotRequired[dict[str, Any]]
    is_verified: NotRequired[bool]
    retry_count: NotRequired[int]


__all__ = ["MiningAgentState"]
