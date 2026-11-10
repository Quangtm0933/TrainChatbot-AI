
"""
Database module for TrainChatbot.

Quản lý kết nối và khởi tạo cơ sở dữ liệu SQLite.
"""

import sqlite3
from pathlib import Path


# Xác định thư mục database
BASE_DIR = Path(__file__).resolve().parent

# Đường dẫn file SQLite
DATABASE_PATH = BASE_DIR / "trainchatbot.db"

# Đường dẫn file cấu trúc bảng
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection():
    """
    Tạo kết nối đến SQLite.

    Trả về:
        Đối tượng kết nối SQLite.
    """

    connection = sqlite3.connect(DATABASE_PATH)

    # Cho phép SQLite kiểm tra khóa ngoại
    connection.execute("PRAGMA foreign_keys = ON")

    # Trả kết quả truy vấn theo dạng có thể truy cập bằng tên cột
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """
    Khởi tạo database và tạo các bảng nếu chưa tồn tại.
    """

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file schema: {SCHEMA_PATH}"
        )

    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_connection() as connection:
        connection.executescript(schema)

    print("Database initialized successfully.")


if __name__ == "__main__":
    initialize_database()
