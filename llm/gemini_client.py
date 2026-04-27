import os

from dotenv import load_dotenv
import google.generativeai as genai

from config import GEMINI_API_KEY_ENV, GEMINI_MODEL_NAME


def _get_api_key():
    load_dotenv()
    api_key = os.getenv(GEMINI_API_KEY_ENV)
    if not api_key:
        raise ValueError(
            f"Missing {GEMINI_API_KEY_ENV}. Set it in your environment before running."
        )
    return api_key


def get_gemini_model():
    api_key = _get_api_key()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(GEMINI_MODEL_NAME)


def generate_text(prompt, temperature=0.2):
    model = get_gemini_model()
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": temperature,
        },
    )
    return response.text or ""
