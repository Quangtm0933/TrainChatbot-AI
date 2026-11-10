
import pytest

from utils.intent_classifier import (
    classify_intent,
    normalize_text,
)


@pytest.mark.parametrize(
    "question, expected",
    [
        ("Xin chào", "greeting"),
        ("Hello", "greeting"),
        ("Giá vé tàu Hà Nội đi Huế bao nhiêu?",
         "ticket_price"),
        ("Tôi muốn đổi vé tàu", "ticket_policy"),
        ("Tìm chuyến tàu Hà Nội đi Huế",
         "search_schedule"),
        ("Tôi muốn đi từ Hà Nội đến Huế",
         "search_route"),
        ("Tư vấn lịch trình du lịch Huế",
         "travel_advice"),
        ("Hôm nay thời tiết thế nào?", "other"),
        ("", "other"),
    ],
)
def test_classify_intent(question, expected):
    assert classify_intent(question) == expected


def test_normalize_vietnamese():
    assert normalize_text("Đường Sắt Việt Nam") == (
        "duong sat viet nam"
    )


def test_empty_text():
    assert classify_intent("   ") == "other"


def test_invalid_input():
    with pytest.raises(TypeError):
        classify_intent(None)
