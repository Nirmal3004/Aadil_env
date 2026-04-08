from openai import OpenAI

from config import API_BASE_URL, API_KEY, MODEL_NAME


def get_openai_client() -> OpenAI:
    return OpenAI(
        api_key=API_KEY,
        base_url=API_BASE_URL,
    )


def ping_llm_proxy() -> None:
    if not API_KEY:
        return

    client = get_openai_client()
    client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": "Reply with OK.",
            }
        ],
        max_tokens=1,
        temperature=0,
    )
