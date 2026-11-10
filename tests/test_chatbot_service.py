
import pytest

import database.database as database_module
import database.seed_data as seed_module

from services.chatbot_service import process_message


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Khởi tạo database riêng với dữ liệu mẫu."""

    temporary_db = tmp_path / "test_chatbot.db"

    monkeypatch.setattr(
        database_module,
        "DATABASE_PATH",
        temporary_db
    )

    database_module.initialize_database()
    seed_module.seed_database()

    return temporary_db


def test_greeting(test_db):
    result = process_message("Xin chào")

    assert result["intent"] == "greeting"
    assert "Xin chào" in result["response"]


def test_search_schedule_success(test_db):
    result = process_message(
        "Tôi muốn đi từ Hà Nội đến Huế ngày 20/12/2026"
    )

    assert result["intent"] == "search_schedule"
    assert result["data"] is not None
    assert len(result["data"]) == 1
    assert result["data"][0]["train_name"] == "SE1"
    assert result["needs_followup"] is False


def test_ticket_price_success(test_db):
    result = process_message(
        "Giá vé tàu từ Hà Nội đến Huế ngày 20/12/2026"
    )

    assert result["intent"] == "ticket_price"
    assert result["data"] is not None
    assert "450,000 VNĐ" in result["response"]
    assert "650,000 VNĐ" in result["response"]


def test_missing_station(test_db):
    result = process_message(
        "Tôi muốn tra cứu lịch tàu ngày 20/12/2026"
    )

    assert result["data"] is None
    assert result["needs_followup"] is True


def test_missing_travel_date(test_db):
    result = process_message(
        "Tôi muốn đi từ Hà Nội đến Huế"
    )

    assert result["data"] is None
    assert result["needs_followup"] is True
    assert "ngày nào" in result["response"]


def test_schedule_not_found(test_db):
    result = process_message(
        "Tôi muốn đi từ Hà Nội đến Huế ngày 21/12/2026"
    )

    assert result["data"] == []
    assert "chưa tìm thấy" in result["response"]


def test_ticket_policy(test_db):
    result = process_message(
        "Tôi muốn hỏi quy định đổi trả vé tàu"
    )

    assert result["intent"] == "ticket_policy"
    assert "chính thức" in result["response"]


def test_empty_message(test_db):
    result = process_message("")

    assert result["intent"] == "other"
    assert result["needs_followup"] is True


def test_invalid_message_type(test_db):
    with pytest.raises(TypeError):
        process_message(123)
