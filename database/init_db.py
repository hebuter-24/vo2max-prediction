"""
数据库初始化脚本
"""
import os
import sqlite3
from pathlib import Path


def _get_base_path() -> Path:
    """获取项目根目录的绝对路径（兼容打包环境）"""
    import sys as _sys
    if getattr(_sys, 'frozen', False) and hasattr(_sys, '_MEIPASS'):
        base = Path(os.path.abspath(os.path.dirname(_sys.executable)))
    else:
        base = Path(os.path.abspath(os.path.dirname(__file__))).parent
    return base


def _get_db_connection():
    """获取数据库连接，支持 Hugging Face Spaces"""
    if os.environ.get('SPACE_ID'):
        return sqlite3.connect(':memory:', check_same_thread=False)
    else:
        db_path = _get_base_path() / "vo2max_prediction.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(str(db_path))


DB_PATH = _get_base_path() / "vo2max_prediction.db"


def init_database():
    """初始化数据库表结构"""
    conn = _get_db_connection()
    cursor = conn.cursor()

    # 创建用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 创建预测记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prediction_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            age INTEGER NOT NULL,
            sex TEXT NOT NULL,
            height REAL NOT NULL,
            weight REAL NOT NULL,
            rest_hr INTEGER NOT NULL,
            max_hr INTEGER NOT NULL,
            vo2max REAL NOT NULL,
            percentile INTEGER NOT NULL,
            level TEXT NOT NULL,
            plan_html TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    # 创建索引以提高查询性能
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON prediction_records(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON prediction_records(created_at)")

    conn.commit()
    conn.close()
    if os.environ.get('SPACE_ID'):
        print("数据库初始化完成: :memory: (Hugging Face Spaces)")
    else:
        print(f"数据库初始化完成: {DB_PATH}")


if __name__ == "__main__":
    init_database()
