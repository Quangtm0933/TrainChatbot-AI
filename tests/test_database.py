
import sqlite3

import pytest

import database.database as database_module


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """
    Tạo database tạm riêng cho mỗi bài kiểm thử.
    Tránh ảnh hưởng đến database chính của dự án.
    """

    temporary_db = tmp_path / "test_trainchatbot.db"

    monkeypatch.setattr(
        database_module,
        "DATABASE_PATH",
        temporary_db
    )

    database_module.initialize_database()

    return temporary_db


def test_database_initialization(test_db):
    """Kiểm tra database có đủ 5 bảng."""

    with database_module.get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)

        tables = [row["name"] for row in cursor.fetchall()]

    expected_tables = [
        "routes",
        "schedules",
        "stations",
        "ticket_prices",
        "trains",
    ]

    assert tables == expected_tables


def test_foreign_keys_enabled(test_db):
    """Kiểm tra cơ chế khóa ngoại được bật."""

    with database_module.get_connection() as connection:
        result = connection.execute(
            "PRAGMA foreign_keys"
        ).fetchone()

    assert result[0] == 1


def test_foreign_key_rejects_invalid_station(test_db):
    """Không cho phép tuyến đường tham chiếu ga không tồn tại."""

    with database_module.get_connection() as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("""
                INSERT INTO routes (
                    departure_station_id,
                    arrival_station_id
                )
                VALUES (999, 1000)
            """)


def test_ticket_price_rejects_negative_value(test_db):
    """Không cho phép giá vé âm."""

    with database_module.get_connection() as connection:
        # Tạo dữ liệu hợp lệ trước khi kiểm tra giá vé
        connection.execute("""
            INSERT INTO stations (station_name, province)
            VALUES ('Hà Nội', 'Hà Nội')
        """)

        connection.execute("""
            INSERT INTO stations (station_name, province)
            VALUES ('Huế', 'Thừa Thiên Huế')
        """)

        connection.execute("""
            INSERT INTO routes (
                departure_station_id,
                arrival_station_id
            )
            VALUES (1, 2)
        """)

        connection.execute("""
            INSERT INTO trains (train_name)
            VALUES ('SE1')
        """)

        connection.execute("""
            INSERT INTO schedules (
                train_id,
                route_id,
                travel_date,
                departure_time,
                arrival_time
            )
            VALUES (1, 1, '2026-12-20', '19:00', '08:00')
        """)

        # Thử thêm giá vé âm vào lịch tàu hợp lệ
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("""
                INSERT INTO ticket_prices (
                    schedule_id,
                    seat_type,
                    price
                )
                VALUES (1, 'Ghế mềm', -1000)
            """)
