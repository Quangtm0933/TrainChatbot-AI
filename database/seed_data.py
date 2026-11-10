
"""
Seed Data for TrainChatbot.

Thêm dữ liệu mẫu vào SQLite:
- Nhà ga
- Tuyến đường
- Đoàn tàu
- Lịch tàu
- Giá vé

Lưu ý: Đây là dữ liệu giả lập để phát triển và kiểm thử,
không phải lịch chạy hoặc giá vé thực tế.
"""

from database.database import (
    get_connection,
    initialize_database,
)


# =========================================
# 1. DỮ LIỆU NHÀ GA
# =========================================

STATIONS = [
    ("Hà Nội", "Hà Nội"),
    ("Đồng Hới", "Quảng Bình"),
    ("Huế", "Thừa Thiên Huế"),
    ("Đà Nẵng", "Đà Nẵng"),
    ("Nha Trang", "Khánh Hòa"),
    ("Sài Gòn", "TP. Hồ Chí Minh"),
]


# =========================================
# 2. DỮ LIỆU TUYẾN ĐƯỜNG
# =========================================

ROUTES = [
    ("Hà Nội", "Đồng Hới", 522),
    ("Hà Nội", "Huế", 688),
    ("Hà Nội", "Đà Nẵng", 791),
    ("Huế", "Đà Nẵng", 103),
    ("Đà Nẵng", "Nha Trang", 524),
    ("Đà Nẵng", "Sài Gòn", 935),
]


# =========================================
# 3. DỮ LIỆU ĐOÀN TÀU
# =========================================

TRAINS = [
    ("SE1", "Tàu thống nhất Bắc - Nam"),
    ("SE3", "Tàu thống nhất Bắc - Nam"),
    ("SE5", "Tàu thống nhất Bắc - Nam"),
    ("SE7", "Tàu thống nhất Bắc - Nam"),
]


# =========================================
# 4. DỮ LIỆU LỊCH TÀU
# =========================================

SCHEDULES = [
    ("SE1", "Hà Nội", "Huế", "2026-12-20", "19:30", "08:00"),
    ("SE3", "Hà Nội", "Đà Nẵng", "2026-12-20", "19:00", "11:30"),
    ("SE5", "Hà Nội", "Đồng Hới", "2026-12-20", "09:00", "18:30"),
    ("SE7", "Huế", "Đà Nẵng", "2026-12-20", "08:00", "10:45"),
]


# =========================================
# 5. DỮ LIỆU GIÁ VÉ
# =========================================

TICKET_PRICES = [
    ("SE1", "Hà Nội", "Huế", "Ghế mềm", 450000),
    ("SE1", "Hà Nội", "Huế", "Giường nằm", 650000),

    ("SE3", "Hà Nội", "Đà Nẵng", "Ghế mềm", 520000),
    ("SE3", "Hà Nội", "Đà Nẵng", "Giường nằm", 780000),

    ("SE5", "Hà Nội", "Đồng Hới", "Ghế mềm", 300000),
    ("SE5", "Hà Nội", "Đồng Hới", "Giường nằm", 480000),

    ("SE7", "Huế", "Đà Nẵng", "Ghế mềm", 120000),
    ("SE7", "Huế", "Đà Nẵng", "Giường nằm", 220000),
]


def get_station_id(connection, station_name):
    """Lấy ID nhà ga theo tên."""

    row = connection.execute(
        """
        SELECT station_id
        FROM stations
        WHERE station_name = ?
        """,
        (station_name,),
    ).fetchone()

    return row["station_id"]


def get_route_id(connection, departure, arrival):
    """Lấy ID tuyến đường theo ga đi và ga đến."""

    departure_id = get_station_id(connection, departure)
    arrival_id = get_station_id(connection, arrival)

    row = connection.execute(
        """
        SELECT route_id
        FROM routes
        WHERE departure_station_id = ?
          AND arrival_station_id = ?
        """,
        (departure_id, arrival_id),
    ).fetchone()

    return row["route_id"]


def get_train_id(connection, train_name):
    """Lấy ID đoàn tàu theo tên."""

    row = connection.execute(
        """
        SELECT train_id
        FROM trains
        WHERE train_name = ?
        """,
        (train_name,),
    ).fetchone()

    return row["train_id"]


def seed_database():
    """Thêm dữ liệu mẫu vào database."""

    with get_connection() as connection:

        # 1. Thêm nhà ga
        connection.executemany(
            """
            INSERT OR IGNORE INTO stations (
                station_name,
                province
            )
            VALUES (?, ?)
            """,
            STATIONS,
        )

        # 2. Thêm tuyến đường
        for departure, arrival, distance in ROUTES:
            departure_id = get_station_id(
                connection, departure
            )

            arrival_id = get_station_id(
                connection, arrival
            )

            connection.execute(
                """
                INSERT OR IGNORE INTO routes (
                    departure_station_id,
                    arrival_station_id,
                    distance_km
                )
                VALUES (?, ?, ?)
                """,
                (departure_id, arrival_id, distance),
            )

        # 3. Thêm đoàn tàu
        connection.executemany(
            """
            INSERT OR IGNORE INTO trains (
                train_name,
                description
            )
            VALUES (?, ?)
            """,
            TRAINS,
        )

        # 4. Thêm lịch tàu
        for (
            train_name,
            departure,
            arrival,
            travel_date,
            departure_time,
            arrival_time,
        ) in SCHEDULES:

            train_id = get_train_id(
                connection, train_name
            )

            route_id = get_route_id(
                connection, departure, arrival
            )

            connection.execute(
                """
                INSERT OR IGNORE INTO schedules (
                    train_id,
                    route_id,
                    travel_date,
                    departure_time,
                    arrival_time
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    train_id,
                    route_id,
                    travel_date,
                    departure_time,
                    arrival_time,
                ),
            )

        # 5. Thêm giá vé
        for (
            train_name,
            departure,
            arrival,
            seat_type,
            price,
        ) in TICKET_PRICES:

            train_id = get_train_id(
                connection, train_name
            )

            route_id = get_route_id(
                connection, departure, arrival
            )

            schedule = connection.execute(
                """
                SELECT schedule_id
                FROM schedules
                WHERE train_id = ?
                  AND route_id = ?
                  AND travel_date = '2026-12-20'
                """,
                (train_id, route_id),
            ).fetchone()

            connection.execute(
                """
                INSERT OR IGNORE INTO ticket_prices (
                    schedule_id,
                    seat_type,
                    price
                )
                VALUES (?, ?, ?)
                """,
                (schedule["schedule_id"], seat_type, price),
            )

    print("Sample data inserted successfully.")


if __name__ == "__main__":
    initialize_database()
    seed_database()
