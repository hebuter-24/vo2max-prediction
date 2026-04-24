"""
数据库增删改查操作
"""
import hashlib
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from .models import User, PredictionRecord
from .connection import get_db


def safe_float(value, default: float = 0.0) -> float:
    """安全地将值转换为 float，处理 bytes、None、numpy 类型等"""
    if value is None:
        return default
    # 已为原生 float
    if isinstance(value, float):
        return value
    # 整数转 float
    if isinstance(value, int):
        return float(value)
    # 字符串转 float
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    # bytes 类型处理
    if isinstance(value, bytes):
        # 1) 尝试 UTF-8 解码（适用于字符串形式的数字）
        try:
            return float(value.decode('utf-8').strip())
        except (ValueError, UnicodeDecodeError):
            pass
        # 2) 尝试直接 struct 解包（适用于 8 字节 IEEE 754 双精度浮点）
        try:
            import struct
            if len(value) == 8:  # 双精度浮点标准 8 字节
                return struct.unpack('d', value)[0]
        except (ValueError, struct.error):
            pass
        # 3) 尝试 numpy 方式解码（如果可用）
        try:
            import numpy as np
            arr = np.frombuffer(value, dtype=np.float64)
            if len(arr) > 0:
                return float(arr[0])
        except Exception:
            pass
        return default
    # 其他类型（包括 numpy 类型）尝试直接 float()
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default: int = 0) -> int:
    """安全地将值转换为 int，处理 bytes、None、numpy 类型等"""
    if value is None:
        return default
    # 已为原生 int
    if isinstance(value, int):
        return value
    # 浮点取整
    if isinstance(value, float):
        return int(value)
    # 字符串转 int
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return default
    # bytes 类型处理
    if isinstance(value, bytes):
        try:
            return int(value.decode('utf-8').strip())
        except (ValueError, UnicodeDecodeError):
            return default
    # 其他类型尝试直接 int()
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_str(value, default: str = "") -> str:
    """安全地将值转换为 str，处理 bytes、None、numpy 类型等"""
    if value is None:
        return default
    # 已为原生 str
    if isinstance(value, str):
        return value
    # bytes 直接 decode
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    # 其他类型转 str
    return str(value)


def hash_password(password: str) -> str:
    """对密码进行哈希处理"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username: str, password: str) -> Optional[User]:
    """创建新用户"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                (username, hash_password(password), datetime.now().isoformat())
            )
            conn.commit()
            user_id = cursor.lastrowid
            return get_user_by_id(user_id)
        except sqlite3.IntegrityError:
            return None


def get_user_by_username(username: str) -> Optional[User]:
    """根据用户名获取用户"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            return User(
                id=safe_int(row["id"]),
                username=safe_str(row["username"]),
                password_hash=safe_str(row["password_hash"]),
                created_at=datetime.fromisoformat(safe_str(row["created_at"]))
            )
    return None


def get_user_by_id(user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return User(
                id=safe_int(row["id"]),
                username=safe_str(row["username"]),
                password_hash=safe_str(row["password_hash"]),
                created_at=datetime.fromisoformat(safe_str(row["created_at"]))
            )
    return None


def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    return hash_password(password) == password_hash


def create_prediction(
    user_id: int,
    age: int,
    sex: str,
    height: float,
    weight: float,
    rest_hr: int,
    max_hr: int,
    vo2max: float,
    percentile: int,
    level: str,
    plan_html: str
) -> PredictionRecord:
    """创建一条预测记录"""
    with get_db() as conn:
        cursor = conn.cursor()
        # 确保所有数值都是 Python 原生类型
        cursor.execute(
            """INSERT INTO prediction_records
               (user_id, age, sex, height, weight, rest_hr, max_hr, vo2max, percentile, level, plan_html, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                int(user_id),
                int(age),
                str(sex),
                float(height),
                float(weight),
                int(rest_hr),
                int(max_hr),
                float(vo2max),
                int(percentile),
                str(level),
                str(plan_html),
                datetime.now().isoformat()
            )
        )
        conn.commit()
        record_id = cursor.lastrowid
        return get_prediction_by_id(record_id)


def get_prediction_by_id(record_id: int) -> Optional[PredictionRecord]:
    """根据ID获取预测记录"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM prediction_records WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        if row:
            return PredictionRecord(
                id=safe_int(row["id"]),
                user_id=safe_int(row["user_id"]),
                age=safe_int(row["age"]),
                sex=safe_str(row["sex"]),
                height=safe_float(row["height"]),
                weight=safe_float(row["weight"]),
                rest_hr=safe_int(row["rest_hr"]),
                max_hr=safe_int(row["max_hr"]),
                vo2max=safe_float(row["vo2max"]),
                percentile=safe_int(row["percentile"]),
                level=safe_str(row["level"]),
                plan_html=safe_str(row["plan_html"]),
                created_at=datetime.fromisoformat(safe_str(row["created_at"]))
            )
    return None


def get_user_predictions(user_id: int, limit: int = 50) -> List[PredictionRecord]:
    """获取用户的所有预测记录（按时间倒序）"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM prediction_records WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (int(user_id), limit)
        )
        rows = cursor.fetchall()
        return [
            PredictionRecord(
                id=safe_int(row["id"]),
                user_id=safe_int(row["user_id"]),
                age=safe_int(row["age"]),
                sex=safe_str(row["sex"]),
                height=safe_float(row["height"]),
                weight=safe_float(row["weight"]),
                rest_hr=safe_int(row["rest_hr"]),
                max_hr=safe_int(row["max_hr"]),
                vo2max=safe_float(row["vo2max"]),
                percentile=safe_int(row["percentile"]),
                level=safe_str(row["level"]),
                plan_html=safe_str(row["plan_html"]),
                created_at=datetime.fromisoformat(safe_str(row["created_at"]))
            )
            for row in rows
        ]


def get_user_prediction_stats(user_id: int) -> Dict[str, Any]:
    """获取用户预测统计信息"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) as total, AVG(vo2max) as avg_vo2max, MAX(vo2max) as max_vo2max, MIN(vo2max) as min_vo2max FROM prediction_records WHERE user_id = ?",
            (int(user_id),)
        )
        row = cursor.fetchone()
        return {
            "total": safe_int(row["total"]),
            "avg_vo2max": round(safe_float(row["avg_vo2max"]), 2),
            "max_vo2max": round(safe_float(row["max_vo2max"]), 2),
            "min_vo2max": round(safe_float(row["min_vo2max"]), 2),
        }