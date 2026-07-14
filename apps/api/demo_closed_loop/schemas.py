from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


DemoStepStatus = Literal[
    "pending",
    "passed",
    "failed",
]


class P101DemoStep(BaseModel):
    step_id: str
    title: str
    status: DemoStepStatus
    description: str
    evidence_used: list[str] = Field(
        default_factory=list
    )
    ai_confidence: float | None = None
    human_approval_required: bool
    linked_endpoint: str
    timestamp: str | None = None


class P101ClosedLoopState(BaseModel):
    demo_id: str
    asset_id: str
    asset_name: str
    status: Literal[
        "not_started",
        "running",
        "completed",
    ]
    current_step: int
    total_steps: int
    completed_steps: int
    summary: str
    judge_message: str
    steps: list[P101DemoStep]


class P101ClosedLoopTimelineResponse(BaseModel):
    demo_id: str
    asset_id: str
    timeline: list[P101DemoStep]


class P101ClosedLoopRunResponse(BaseModel):
    state: P101ClosedLoopState
