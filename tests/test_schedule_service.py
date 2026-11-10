
import pytest

import database.database as database_module
import database.seed_data as seed_module

from services.schedule_service import search_schedules


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Tạo database riêng và nạp dữ liệu mẫu cho mỗi bài test."""

    temporary_db = tmp_path / "test_schedule.db"

    monkeypatch.setattr(
        database_module,
        "DATABASE_PATH",
        temporary_db
    )

    database_module.initialize_database()
    seed_module.seed_database()

    return temporary_db


def test_search_existing_schedule(test_db):
    """Tìm được chuyến tàu Hà Nội - Huế."""

    results = search_schedules(
        "Hà Nội",
        "Huế",
        "2026-12-20"
    )

    assert len(results) == 1

    schedule = results[0]

    assert schedule["train_name"] == "SE1"
    assert schedule["departure_station"] == "Hà Nội"
    assert schedule["arrival_station"] == "Huế"
    assert schedule["departure_time"] == "19:30"
    assert schedule["arrival_time"] == "08:00"


def test_search_schedule_prices(test_db):
    """Kiểm tra thông tin các loại vé."""

    results = search_schedules(
        "Hà Nội",
        "Huế",
        "2026-12-20"
    )

    prices = results[0]["prices"]

    assert len(prices) == 2

    price_dict = {
        item["seat_type"]: item["price"]
        for item in prices
    }

    assert price_dict["Ghế mềm"] == 450000
    assert price_dict["Giường nằm"] == 650000


def test_search_nonexistent_schedule(test_db):
    """Không tìm thấy lịch tàu phù hợp."""

    results = search_schedules(
        "Hà Nội",
        "Huế",
        "2026-12-21"
    )

    assert results == []


def test_search_empty_station(test_db):
    """Không cho phép bỏ trống tên ga."""

    with pytest.raises(ValueError):
        search_schedules(
            "",
            "Huế",
            "2026-12-20"
        )


def test_search_same_station(test_db):
    """Không cho phép ga đi và ga đến trùng nhau."""

    with pytest.raises(ValueError):
        search_schedules(
            "Hà Nội",
            "Hà Nội",
            "2026-12-20"
        )


def test_search_invalid_date(test_db):
    """Không chấp nhận ngày không tồn tại."""

    with pytest.raises(ValueError):
        search_schedules(
            "Hà Nội",
            "Huế",
            "2026-02-30"
        )


def test_search_invalid_date_format(test_db):
    """Không chấp nhận định dạng ngày sai."""

    with pytest.raises(ValueError):
        search_schedules(
            "Hà Nội",
            "Huế",
            "20/12/2026"
        )


def test_search_invalid_input_type(test_db):
    """Không chấp nhận dữ liệu đầu vào sai kiểu."""

    with pytest.raises(TypeError):
        search_schedules(
            123,
            "Huế",
            "2026-12-20"
        )
