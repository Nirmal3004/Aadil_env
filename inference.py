import requests
from requests import RequestException

from config import ENV_SERVER_URL, MODEL_NAME
from my_env.env import JobReadinessEnv
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


def run_task(task_name):
    log_start(task_name)
    rewards = []

    state = post("/reset", {"task_name": task_name})

    steps = [
        {
            "action_type": "identify_goal",
            "content": "Learn AI tools and skills for job readiness"
        },
        {
            "action_type": "generate_plan",
            "content": [
                "Learn Python and AI basics",
                "Practice SQL, data handling, and beginner machine learning concepts",
                "Build 2 small projects using AI tools",
                "Create resume and portfolio"
            ]
        },
        {
            "action_type": "suggest_tools",
            "content": ["Python", "ChatGPT", "Hugging Face", "GitHub"]
        },
        {
            "action_type": "set_timeline",
            "content": "4-month beginner-friendly roadmap with weekly goals"
        },
        {
            "action_type": "finalize",
            "content": "done"
        },
    ]

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
