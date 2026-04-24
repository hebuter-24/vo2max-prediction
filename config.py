"""
应用配置
"""
import os
from pathlib import Path

# 项目根目录（使用 __file__ 的绝对路径，确保任意运行目录都能正确解析）
ROOT_DIR = Path(os.path.abspath(os.path.dirname(__file__)))

# 模型文件路径
MODEL_PATH = ROOT_DIR / "model" / "xgboost_vo2max.pkl"

# 数据库路径
DB_PATH = ROOT_DIR / "vo2max_prediction.db"

# 训练数据路径（可选）
DATA_PATH = ROOT_DIR / "data" / "1.xlsx"

# Streamlit 配置
PAGE_TITLE = "VO₂max 智能预测系统"
PAGE_ICON = "🏃‍♂️"
LAYOUT = "wide"

# 分页设置
PAGES = {
    "home": "🏠 首页",
    "prediction": "🏃 心肺预测",
    "profile": "📋 健康档案",
    "analysis": "📈 数据分析",
}

# 默认页面
DEFAULT_PAGE = "home"
