
"""
Intent Classifier for TrainChatbot.

Phân loại ý định người dùng bằng phương pháp Rule-based.
Không cần Gemini API hoặc thư viện bên ngoài.
"""

import re
import unicodedata


# Các nhãn ý định được hỗ trợ
INTENTS = {
    "greeting",
    "ticket_price",
    "search_schedule",
    "search_route",
    "travel_advice",
    "ticket_policy",
    "other",
}


def normalize_text(text: str) -> str:
    """
    Chuẩn hóa văn bản tiếng Việt:
    - Chuyển thành chữ thường.
    - Loại bỏ dấu tiếng Việt.
    - Chuyển đ thành d.
    - Loại bỏ ký tự đặc biệt.
    - Chuẩn hóa khoảng trắng.
    """

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    text = text.lower().strip()
    text = text.replace("đ", "d")

    # Tách dấu tiếng Việt khỏi ký tự gốc
    text = unicodedata.normalize("NFD", text)

    # Loại bỏ các dấu thanh
    text = "".join(
        char
        for char in text
        if unicodedata.category(char) != "Mn"
    )

    # Thay dấu câu bằng khoảng trắng
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Loại bỏ khoảng trắng thừa
    text = re.sub(r"\s+", " ", text).strip()

    return text


def contains_keyword(text: str, keywords: list[str]) -> bool:
    """Kiểm tra xem văn bản có chứa từ khóa hay không."""

    return any(keyword in text for keyword in keywords)


def classify_intent(text: str) -> str:
    """
    Phân loại ý định người dùng bằng Rule-based.

    Ưu tiên:
    1. Chào hỏi
    2. Giá vé
    3. Chính sách vé
    4. Tư vấn lịch trình
    5. Lịch tàu
    6. Tuyến đường
    7. Khác
    """

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    normalized = normalize_text(text)

    if not normalized:
        return "other"

    # 1. Chào hỏi
    greeting_patterns = [
        r"^(xin chao|chao ban|chao|hello|hi|hey)( ban)?$",
        r"^(good morning|good afternoon|good evening)$",
    ]

    if any(
        re.search(pattern, normalized)
        for pattern in greeting_patterns
    ):
        return "greeting"

    # 2. Hỏi giá vé
    price_keywords = [
        "gia ve",
        "gia tien ve",
        "ve tau bao nhieu",
        "bao nhieu tien ve",
        "gia giuong nam",
        "gia ghe ngoi",
        "gia khoang",
    ]

    if contains_keyword(normalized, price_keywords):
        return "ticket_price"

    # 3. Chính sách vé
    policy_keywords = [
        "doi ve",
        "tra ve",
        "hoan ve",
        "huy ve",
        "quy dinh ve",
        "chinh sach ve",
        "thu tuc doi ve",
        "thu tuc tra ve",
    ]

    if contains_keyword(normalized, policy_keywords):
        return "ticket_policy"

    # 4. Tư vấn lịch trình
    advice_keywords = [
        "tu van lich trinh",
        "goi y lich trinh",
        "lich trinh du lich",
        "sap xep chuyen di",
        "nen di dau",
        "tu van chuyen di",
        "len ke hoach di",
    ]

    if contains_keyword(normalized, advice_keywords):
        return "travel_advice"

    # 5. Nhận diện ngày đi cụ thể
    date_pattern = (
        r"\b(?:"
        r"\d{1,2}/\d{1,2}/\d{4}"
        r"|\d{1,2}-\d{1,2}-\d{4}"
        r"|\d{4}-\d{1,2}-\d{1,2}"
        r")\b"
    )

    has_date = re.search(date_pattern, text) is not None
    date = re.search(date_pattern, normalized) is not None

    # 6. Tìm chuyến tàu / lịch tàu
    schedule_keywords = [
        "lich tau",
        "gio tau",
        "tim tau",
        "tim chuyen tau",
        "chuyen tau",
        "tau nao",
        "tau chay luc nao",
        "tau khoi hanh",
        "co tau nao",
    ]

    if contains_keyword(normalized, schedule_keywords):
        return "search_schedule"

    # Có ngày đi và có yêu cầu di chuyển:
    # ưu tiên tra cứu lịch tàu.
    if has_date and contains_keyword(
        normalized,
        ["di tu", "tu ha noi den", "tu hue den",
         "tu da nang den", "khoi hanh", "di den"]
    ):
        return "search_schedule"

    # 7. Tìm tuyến đường
    route_keywords = [
        "tuyen duong",
        "duong di",
        "di tu",
        "tu ha noi den",
        "tu ha noi di",
        "tu hue den",
        "tu da nang den",
    ]

    if contains_keyword(normalized, route_keywords):
        return "search_route"

    return "other"



    