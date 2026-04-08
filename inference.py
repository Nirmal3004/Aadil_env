import json

import requests
from requests import RequestException

from config import API_KEY, ENV_SERVER_URL, MODEL_NAME
from my_env.env import JobReadinessEnv
from openai_client import get_openai_client

TASKS = ["easy", "medium", "hard"]
LOCAL_ENV = JobReadinessEnv()
USE_LOCAL_ENV = False


def log_start(task):
    print(f"[START] task={task} env=job_readiness_env model={MODEL_NAME}", flush=True)


def log_step(step, action, reward, done, error):
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error or 'null'}",
        flush=True,
    )


def log_end(success, steps, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}",
        flush=True,
    )


def log_mode(mode):
    print(f"[MODE] backend={mode}", flush=True)


def local_post(path, payload):
    if path == "/reset":
        return LOCAL_ENV.reset(payload.get("task_name", "easy")).model_dump()
    if path == "/step":
        return LOCAL_ENV.step(payload).model_dump()
    if path == "/state":
        return LOCAL_ENV.state_dict()
    raise ValueError(f"Unsupported path: {path}")


def post(path, payload):
    url = f"{ENV_SERVER_URL}{path}"
    global USE_LOCAL_ENV

    if USE_LOCAL_ENV:
        return local_post(path, payload)

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except (RequestException, ValueError) as exc:
        USE_LOCAL_ENV = True
        print(
            f"[WARN] API server unavailable at {ENV_SERVER_URL}. Falling back to local environment. error={exc}",
            flush=True,
        )
        log_mode("local")
        return local_post(path, payload)


def default_plan(state):
    user_input = state["user_input"]
    return {
        "goal": f"Create a structured AI job-readiness plan for: {user_input}",
        "plan": [
            "Learn Python fundamentals and AI basics",
            "Practice SQL, data handling, and beginner machine learning concepts",
            "Build 2 practical projects and publish them on GitHub",
            "Prepare a resume, portfolio, and interview practice routine",
        ],
        "tools": ["Python", "ChatGPT", "Hugging Face", "GitHub"],
        "timeline": "4-month beginner-friendly roadmap with weekly goals and project milestones",
    }


def build_messages(state):
    return [
        {
            "role": "system",
            "content": (
                "You are helping solve a job-readiness planning environment. "
                "Return only valid JSON with keys: goal, plan, tools, timeline. "
                "goal must be a short string. plan must be a list of 4 concise steps. "
                "tools must be a list of 3 to 5 items. timeline must be a short string. "
                "Include practical beginner-friendly guidance and keywords like Python, projects, portfolio, "
                "SQL, machine learning, AI tools, timeline, or resume when relevant."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Difficulty: {state['difficulty']}\n"
                f"User input: {state['user_input']}\n"
                f"Feedback: {state['feedback']}\n"
                "Produce the planning JSON now."
            ),
        },
    ]


def generate_plan_with_llm(state):
    if not API_KEY:
        raise RuntimeError("API_KEY is not set.")

    client = get_openai_client()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        response_format={"type": "json_object"},
        messages=build_messages(state),
        temperature=0.2,
    )
    content = response.choices[0].message.content or "{}"
    plan = json.loads(content)

    return {
        "goal": str(plan.get("goal", "")).strip(),
        "plan": [str(item).strip() for item in plan.get("plan", []) if str(item).strip()],
        "tools": [str(item).strip() for item in plan.get("tools", []) if str(item).strip()],
        "timeline": str(plan.get("timeline", "")).strip(),
    }


def build_actions(state):
    try:
        plan_data = generate_plan_with_llm(state)
        log_mode("proxy")
    except Exception as exc:
        print(
            f"[WARN] LLM planning failed. Falling back to deterministic planner. error={exc}",
            flush=True,
        )
        plan_data = default_plan(state)
        log_mode("deterministic")

    return [
        {"action_type": "identify_goal", "content": plan_data["goal"]},
        {"action_type": "generate_plan", "content": plan_data["plan"]},
        {"action_type": "suggest_tools", "content": plan_data["tools"]},
        {"action_type": "set_timeline", "content": plan_data["timeline"]},
        {"action_type": "finalize", "content": "done"},
    ]


def run_task(task_name):
    log_start(task_name)
    rewards = []

    state = post("/reset", {"task_name": task_name})
    steps = build_actions(state)

    success = False
    step_num = 0

    for action in steps:
        step_num += 1
        result = post("/step", action)
        reward = result["reward"]
        done = result["done"]
        error = result.get("error")
        rewards.append(reward)

        log_step(step_num, action["action_type"], reward, done, error)

        if done:
            success = reward >= 0.7
            break

    log_end(success, step_num, rewards)


if __name__ == "__main__":
    for task in TASKS:
        run_task(task)
