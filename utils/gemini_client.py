"""Gemini API client utility module — the API utility layer.

This module isolates all Google Gemini SDK details from the Streamlit UI
in app.py, so the UI layer can call simple functions without knowing SDK
internals (Requirement 8.1, 8.3).

Handles API key loading and communication with the Google Gemini API.
Uses the google-genai SDK (not the deprecated google-generativeai package).

Error handling design: functions in this module intentionally let API
exceptions propagate to the caller. app.py wraps calls in try/except
and displays user-friendly errors, keeping error presentation in the UI
layer where it belongs.
"""

import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Trả lại đúng model bạn đang sử dụng ổn định
MODEL_NAME = "gemini-3.5-flash-lite"


def load_api_key() -> str | None:
    """Load GEMINI_API_KEY from .env file.

    Checks for .env file existence first, then loads it and retrieves
    the API key. This two-step check allows app.py to show distinct
    error messages for "file missing" vs "key not configured".

    Returns:
        The API key string if valid, or None if .env is missing,
        key is unset, empty, or whitespace-only.
    """
    if not os.path.exists(".env"):
        return None

    load_dotenv(".env")

    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None or api_key.strip() == "":
        return None

    return api_key


def send_message(api_key: str, prompt: str, history: list[dict] = None) -> str:
    """Send a prompt with conversation history to Gemini API.

    Automatically retries temporary 503 errors.
    """
    # Xử lý trường hợp history không được truyền vào (mặc định là list rỗng)
    if history is None:
        history = []

    client = genai.Client(api_key=api_key)

    # Chuyển lịch sử hội thoại sang định dạng Gemini
    contents = []

    for msg in history:
        role = "model" if msg["role"] == "assistant" else msg["role"]

        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])],
            )
        )

    # Thêm câu hỏi hiện tại
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        )
    )

    # Gửi yêu cầu, tự động thử lại nếu gặp lỗi 503
    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents
            )

            return response.text

        except Exception as e:
            error_message = str(e).upper()

            # Chỉ thử lại với lỗi máy chủ tạm thời 503
            if "503" in error_message or "UNAVAILABLE" in error_message:

                if attempt < max_attempts - 1:
                    wait_time = 2 ** (attempt + 1)

                    print(
                        f"Gemini đang quá tải. "
                        f"Thử lại sau {wait_time} giây..."
                    )

                    time.sleep(wait_time)
                    continue

            # Các lỗi khác hoặc đã hết số lần thử
            raise