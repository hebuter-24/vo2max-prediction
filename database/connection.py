"""
数据库连接管理模块
"""
import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager


def _get_base_path() -> Path:
    """获取资源根目录的绝对路径（兼容打包环境）"""
    import sys as _sys
    if getattr(_sys, 'frozen', False) and hasattr(_sys, '_MEIPASS'):
        base = Path(os.path.abspath(os.path.dirname(_sys.executable)))
    else:
        base = Path(os.path.abspath(os.path.dirname(__file__))).parent
    return base


DB_PATH = _get_base_path() / "vo2max_prediction.db"


def _is_hf_spaces():
    """检测是否运行在 Hugging Face Spaces"""
    return bool(os.environ.get('SPACE_ID'))


def get_connection():
    """获取数据库连接"""
    if _is_hf_spaces():
        conn = sqlite3.connect(':memory:', check_same_thread=False)
    else:
        conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """上下文管理器：自动处理连接关闭"""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
