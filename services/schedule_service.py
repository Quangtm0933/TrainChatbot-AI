
"""
Schedule service for TrainChatbot.

Cung cấp chức năng tra cứu lịch tàu và giá vé
từ cơ sở dữ liệu SQLite.
"""

from datetime import date

from database.database import get_connection


def search_schedules(
    departure_station: str,
    arrival_station: str,
    travel_date: str
) -> list[dict]:
    """
    Tìm lịch tàu theo ga đi, ga đến và ngày khởi hành.

    Args:
        departure_station: Tên ga đi.
        arrival_station: Tên ga đến.
        travel_date: Ngày đi theo định dạng YYYY-MM-DD.

    Returns:
        Danh sách chuyến tàu, kèm thông tin giá vé.
        Nếu không tìm thấy, trả về danh sách rỗng.
    """

    # 1. Kiểm tra dữ liệu đầu vào
    if not all([
        isinstance(departure_station, str),
        isinstance(arrival_station, str),
        isinstance(travel_date, str)
    ]):
        raise TypeError("Thông tin tra cứu phải là chuỗi.")

    departure_station = departure_station.strip()
    arrival_station = arrival_station.strip()
    travel_date = travel_date.strip()

    if not departure_station or not arrival_station:
        raise ValueError("Ga đi và ga đến không được để trống.")

    if departure_station.casefold() == arrival_station.casefold():
        raise ValueError("Ga đi và ga đến không được trùng nhau.")

    try:
        date.fromisoformat(travel_date)
    except ValueError:
        raise ValueError(
            "Ngày đi không hợp lệ. Hãy sử dụng định dạng YYYY-MM-DD."
        )

    # 2. Truy vấn lịch tàu và giá vé
    query = """
        SELECT
            schedules.schedule_id,
            trains.train_name,
            departure_station.station_name AS departure_station,
            arrival_station.station_name AS arrival_station,
            schedules.travel_date,
            schedules.departure_time,
            schedules.arrival_time,
            routes.distance_km,
            ticket_prices.seat_type,
            ticket_prices.price
        FROM schedules

        JOIN trains
            ON schedules.train_id = trains.train_id

        JOIN routes
            ON schedules.route_id = routes.route_id

        JOIN stations AS departure_station
            ON routes.departure_station_id =
               departure_station.station_id

        JOIN stations AS arrival_station
            ON routes.arrival_station_id =
               arrival_station.station_id

        LEFT JOIN ticket_prices
            ON schedules.schedule_id = ticket_prices.schedule_id

        WHERE departure_station.station_name = ?
          AND arrival_station.station_name = ?
          AND schedules.travel_date = ?

        ORDER BY schedules.departure_time ASC
    """

    with get_connection() as connection:
        rows = connection.execute(
            query,
            (departure_station, arrival_station, travel_date)
        ).fetchall()

    # 3. Gom các loại vé của cùng một chuyến tàu
    schedules = {}

    for row in rows:
        schedule_id = row["schedule_id"]

        if schedule_id not in schedules:
            schedules[schedule_id] = {
                "schedule_id": schedule_id,
                "train_name": row["train_name"],
                "departure_station": row["departure_station"],
                "arrival_station": row["arrival_station"],
                "travel_date": row["travel_date"],
                "departure_time": row["departure_time"],
                "arrival_time": row["arrival_time"],
                "distance_km": row["distance_km"],
                "prices": []
            }

        if row["seat_type"] is not None:
            schedules[schedule_id]["prices"].append({
                "seat_type": row["seat_type"],
                "price": row["price"]
            })

    return list(schedules.values())
