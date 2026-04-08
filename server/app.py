from typing import Any

from fastapi import Body
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
import uvicorn

from my_env.env import JobReadinessEnv

app = FastAPI(title="Job Readiness Task Planner Environment", version="0.2.0")
env = JobReadinessEnv()


class ResetRequest(BaseModel):
    task_name: str = "easy"


class StepRequest(BaseModel):
    action_type: str
    content: Any = ""


@app.get("/")
def root():
    return {"message": "Job Readiness OpenEnv is running"}


@app.get("/reset")
def reset_get():
    state = env.reset("easy")
    return state.model_dump()


@app.post("/reset")
def reset_post(
    req: ResetRequest | None = Body(
        default=None,
        examples={
            "easy": {"summary": "Easy task", "value": {"task_name": "easy"}},
            "medium": {"summary": "Medium task", "value": {"task_name": "medium"}},
            "hard": {"summary": "Hard task", "value": {"task_name": "hard"}},
        },
    )
):
    task_name = "easy" if req is None else req.task_name
    state = env.reset(task_name)
    return state.model_dump()


@app.get("/state")
def get_state():
    if env.state is None:
        raise HTTPException(
            status_code=400,
            detail="Environment not initialized. Call /reset first.",
        )
    return env.state_dict()


@app.get("/step")
def step_get():
    return {
        "message": "Use POST /step with a JSON body containing action_type and content.",
        "state": None if env.state is None else env.state_dict(),
    }


@app.post("/step")
def step_post(
    req: dict[str, Any] | None = Body(
        default=None,
        examples={
            "identify_goal": {
                "summary": "Identify user goal",
                "value": {
                    "action_type": "identify_goal",
                    "content": "Learn AI tools and skills for job readiness",
                },
            },
            "generate_plan": {
                "summary": "Generate a draft plan",
                "value": {
                    "action_type": "generate_plan",
                    "content": [
                        "Learn Python and AI basics",
                        "Practice SQL and beginner ML",
                        "Build 2 projects",
                        "Create resume and portfolio",
                    ],
                },
            },
        },
    )
):
    if req is None:
        raise HTTPException(
            status_code=400,
            detail="Request body is required. Provide action_type and content.",
        )

    action_type = str(req.get("action_type", "")).strip()
    if not action_type:
        raise HTTPException(
            status_code=400,
            detail="action_type is required.",
        )

    try:
        result = env.step(
            {
                "action_type": action_type,
                "content": req.get("content", ""),
            }
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result.model_dump()


def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
