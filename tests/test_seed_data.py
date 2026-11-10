
import database.database as database_module
import database.seed_data as seed_module


def test_seed_data(tmp_path, monkeypatch):
    """Kiểm tra số lượng dữ liệu mẫu được thêm."""

    temporary_db = tmp_path / "test_seed.db"

    monkeypatch.setattr(
        database_module,
        "DATABASE_PATH",
        temporary_db,
    )

    database_module.initialize_database()
    seed_module.seed_database()

    with database_module.get_connection() as connection:
        expected_counts = {
            "stations": 6,
            "routes": 6,
            "trains": 4,
            "schedules": 4,
            "ticket_prices": 8,
        }

        for table, expected_count in expected_counts.items():
            result = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()

            assert result[0] == expected_count


def test_seed_data_is_idempotent(tmp_path, monkeypatch):
    """Chạy seed nhiều lần không tạo dữ liệu trùng."""

    temporary_db = tmp_path / "test_seed_repeat.db"

    monkeypatch.setattr(
        database_module,
        "DATABASE_PATH",
        temporary_db,
    )

    database_module.initialize_database()

    seed_module.seed_database()
    seed_module.seed_database()

    with database_module.get_connection() as connection:
        result = connection.execute(
            "SELECT COUNT(*) FROM stations"
        ).fetchone()

        assert result[0] == 6

        result = connection.execute(
            "SELECT COUNT(*) FROM ticket_prices"
        ).fetchone()

        assert result[0] == 8
