
PRAGMA foreign_keys = ON;

-- 1. Nhà ga
CREATE TABLE IF NOT EXISTS stations (
    station_id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_name TEXT NOT NULL UNIQUE,
    province TEXT
);

-- 2. Tuyến đường
CREATE TABLE IF NOT EXISTS routes (
    route_id INTEGER PRIMARY KEY AUTOINCREMENT,
    departure_station_id INTEGER NOT NULL,
    arrival_station_id INTEGER NOT NULL,
    distance_km REAL,

    FOREIGN KEY (departure_station_id)
        REFERENCES stations(station_id),

    FOREIGN KEY (arrival_station_id)
        REFERENCES stations(station_id),

    UNIQUE (departure_station_id, arrival_station_id),

    CHECK (departure_station_id != arrival_station_id),
    CHECK (distance_km IS NULL OR distance_km > 0)
);

-- 3. Đoàn tàu
CREATE TABLE IF NOT EXISTS trains (
    train_id INTEGER PRIMARY KEY AUTOINCREMENT,
    train_name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- 4. Lịch tàu
CREATE TABLE IF NOT EXISTS schedules (
    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    train_id INTEGER NOT NULL,
    route_id INTEGER NOT NULL,
    travel_date TEXT NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,

    FOREIGN KEY (train_id)
        REFERENCES trains(train_id),

    FOREIGN KEY (route_id)
        REFERENCES routes(route_id),

    CHECK (
        length(travel_date) = 10
        AND travel_date GLOB
        '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
    ),

    CHECK (
        length(departure_time) = 5
        AND departure_time GLOB '[0-2][0-9]:[0-5][0-9]'
        AND substr(departure_time, 1, 2) <= '23'
    ),

    CHECK (
        length(arrival_time) = 5
        AND arrival_time GLOB '[0-2][0-9]:[0-5][0-9]'
        AND substr(arrival_time, 1, 2) <= '23'
    ),

    UNIQUE (train_id, route_id, travel_date, departure_time)
);

-- 5. Giá vé
CREATE TABLE IF NOT EXISTS ticket_prices (
    price_id INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id INTEGER NOT NULL,
    seat_type TEXT NOT NULL,
    price INTEGER NOT NULL,

    FOREIGN KEY (schedule_id)
        REFERENCES schedules(schedule_id),

    CHECK (price >= 0),

    UNIQUE (schedule_id, seat_type)
);
