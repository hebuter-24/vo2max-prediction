"""
工具模块
"""
from .constants import VO2MAX_LEVELS, LEVEL_BG_COLORS, AGE_GROUPS
from .helpers import get_age_group, get_vo2max_level, get_percentile_and_segment, format_table_with_ranges
from .auth import init_session_state, login, register, logout, get_current_user, require_login

__all__ = [
    "VO2MAX_LEVELS",
    "LEVEL_BG_COLORS",
    "AGE_GROUPS",
    "get_age_group",
    "get_vo2max_level",
    "get_percentile_and_segment",
    "format_table_with_ranges",
    "init_session_state",
    "login",
    "register",
    "logout",
    "get_current_user",
    "require_login",
]