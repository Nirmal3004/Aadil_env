from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

from my_env.score_utils import normalize_task_score


class PlannerState(BaseModel):
    task_id: str
    difficulty: str
    user_input: str
    goal: str = ""
    draft_plan: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    timeline: str = ""
    feedback: str = ""
    done: bool = False
    step_count: int = 0
    max_steps: int = 5


class PlannerAction(BaseModel):
    action_type: str
    content: Optional[str] = ""


class StepResult(BaseModel):
    observation: PlannerState
    reward: float
    done: bool
    error: Optional[str] = None

    @field_validator("reward", mode="before")
    @classmethod
    def normalize_reward(cls, value):
        return normalize_task_score(value)
