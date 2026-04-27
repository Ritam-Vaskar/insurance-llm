import os

from dotenv import load_dotenv
from groq import Groq

from config import GROQ_API_KEY_ENV, GROQ_MODEL_NAME


def _get_api_key():
    load_dotenv()
    api_key = os.getenv(GROQ_API_KEY_ENV)
    if not api_key:
        raise ValueError(
            f"Missing {GROQ_API_KEY_ENV}. Set it in your environment before running."
        )
    return api_key


def _get_client():
    api_key = _get_api_key()
    return Groq(api_key=api_key)


def generate_text(prompt, temperature=0.2):
    client = _get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content or ""
