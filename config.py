import os


API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
ENV_SERVER_URL = os.getenv("ENV_SERVER_URL", "http://127.0.0.1:7860")
MODEL_NAME = os.getenv("MODEL_NAME", os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
API_KEY = os.getenv("API_KEY", "")
