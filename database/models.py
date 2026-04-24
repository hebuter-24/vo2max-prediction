"""
数据模型定义
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """用户模型"""
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    created_at: Optional[datetime] = None


@dataclass
class PredictionRecord:
    """预测记录模型"""
    id: Optional[int] = None
    user_id: int = 0
    age: int = 0
    sex: str = ""
    height: float = 0.0
    weight: float = 0.0
    rest_hr: int = 0
    max_hr: int = 0
    vo2max: float = 0.0
    percentile: int = 0
    level: str = ""
    plan_html: str = ""
    created_at: Optional[datetime] = None
