
"""
Entity Extractor for TrainChatbot.

Trích xuất ga đi, ga đến, ngày khởi hành và số hành khách.
Phiên bản đầu sử dụng danh sách ga và Regex.
"""

import re
import unicodedata
from datetime import date


# Danh sách ga thử nghiệm.
# Sẽ chuyển sang lấy dữ liệu từ SQLite ở giai đoạn tiếp theo.
STATION_ALIASES = {
    "ha noi": "Hà Nội",
    "ga ha noi": "Hà Nội",
    "hue": "Huế",
    "ga hue": "Huế",
    "da nang": "Đà Nẵng",
    "ga da nang": "Đà Nẵng",
    "nha trang": "Nha Trang",
    "ga nha trang": "Nha Trang",
    "sai gon": "Sài Gòn",
    "ga sai gon": "Sài Gòn",
    "dong hoi": "Đồng Hới",
    "vinh": "Vinh",
}


def normalize_text(text: str) -> str:
    """Chuyển văn bản về chữ thường và bỏ dấu tiếng Việt."""

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    text = text.lower().strip()
    text = text.replace("đ", "d")
    text = unicodedata.normalize("NFD", text)

    text = "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )

    text = re.sub(r"\s+", " ", text)

    return text


def extract_stations(text: str) -> dict:
    """Nhận diện ga đi và ga đến linh hoạt hơn."""

    normalized = normalize_text(text)

    # 1. Nhận diện cấu trúc đầy đủ trước: từ [ga đi] đến [ga đến]
    match = re.search(
        r"\btu\s+(.+?)\s+den\s+(.+?)(?=\s+ngay\b|\s+vao\b|$)",
        normalized
    )

    if match:
        departure_text = match.group(1).strip()
        arrival_text = match.group(2).strip()
        return {
            "departure_station": STATION_ALIASES.get(departure_text),
            "arrival_station": STATION_ALIASES.get(arrival_text),
        }

    # 2. Nếu câu ngắn (không có từ... đến...), vét cạn tìm ga lẻ
    found_stations = []
    for alias, real_name in STATION_ALIASES.items():
        # Tìm từ khóa xuất hiện trong câu
        if re.search(rf"\b{alias}\b", normalized):
            if real_name not in [s["name"] for s in found_stations]:
                # Lưu lại vị trí để biết ga nào nhắc trước
                found_stations.append({
                    "name": real_name, 
                    "pos": normalized.find(alias)
                })

    # Sắp xếp ga theo thứ tự xuất hiện trong câu
    found_stations.sort(key=lambda x: x["pos"])
    extracted = [s["name"] for s in found_stations]

    if len(extracted) == 1:
        # Nhắc 1 ga: Có chữ "từ" thì là ga đi, còn lại mặc định là ga đến
        if "tu " in normalized or "xuat phat" in normalized:
            return {"departure_station": extracted[0], "arrival_station": None}
        else:
            return {"departure_station": None, "arrival_station": extracted[0]}
            
    elif len(extracted) >= 2:
        # Nhắc 2 ga nhưng nói tắt (VD: "Hà Nội Đà Nẵng"): Ga trước là đi, sau là đến
        return {"departure_station": extracted[0], "arrival_station": extracted[1]}

    return {
        "departure_station": None,
        "arrival_station": None,
    }

def extract_travel_date(text: str) -> str | None:
    """
    Nhận diện ngày theo định dạng:
    - 20/12/2026
    - 20-12-2026
    - 2026-12-20

    Trả về ngày theo định dạng YYYY-MM-DD.
    """

    patterns = [
        r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b",
        r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b",
    ]

    normalized = normalize_text(text)

    for index, pattern in enumerate(patterns):
        match = re.search(pattern, normalized)

        if not match:
            continue

        try:
            if index == 0:
                day, month, year = map(int, match.groups())
            else:
                year, month, day = map(int, match.groups())

            result = date(year, month, day)

            return result.isoformat()

        except ValueError:
            return None

    return None


def extract_passengers(text: str) -> int | None:
    """Nhận diện số lượng hành khách."""

    normalized = normalize_text(text)

    patterns = [
        r"\b(\d+)\s*(?:nguoi|hanh khach)\b",
        r"\b(?:cho|ve cho)\s*(\d+)\s*(?:nguoi|hanh khach)?\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized)

        if match:
            number = int(match.group(1))

            if 1 <= number <= 20:
                return number

    return None


def extract_entities(text: str) -> dict:
    """Trích xuất toàn bộ thông tin cần thiết từ câu hỏi."""

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    stations = extract_stations(text)

    return {
        "departure_station": stations["departure_station"],
        "arrival_station": stations["arrival_station"],
        "travel_date": extract_travel_date(text),
        "passengers": extract_passengers(text),
    }
