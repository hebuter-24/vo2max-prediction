"""
认证相关工具函数
"""
import streamlit as st
from typing import Optional
from database.crud import (
    create_user,
    get_user_by_username,
    verify_password,
    get_user_by_id
)
from database.models import User


def init_session_state():
    """初始化 session state"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "username" not in st.session_state:
        st.session_state.username = ""


def login(username: str, password: str) -> bool:
    """用户登录"""
    user = get_user_by_username(username)
    if user and verify_password(password, user.password_hash):
        st.session_state.logged_in = True
        st.session_state.user = user
        st.session_state.username = username
        return True
    return False


def register(username: str, password: str) -> tuple[bool, str]:
    """用户注册
    返回: (是否成功, 消息)
    """
    if len(username) < 3:
        return False, "用户名至少需要3个字符"
    if len(password) < 6:
        return False, "密码至少需要6个字符"

    existing_user = get_user_by_username(username)
    if existing_user:
        return False, "用户名已存在"

    user = create_user(username, password)
    if user:
        # 自动登录
        st.session_state.logged_in = True
        st.session_state.user = user
        st.session_state.username = username
        return True, "注册成功！"
    return False, "注册失败，请稍后重试"


def logout():
    """用户登出"""
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.username = ""


def get_current_user() -> Optional[User]:
    """获取当前登录用户"""
    return st.session_state.get("user")


def require_login(redirect_page: str = "🏃 心肺预测"):
    """检查是否已登录，未登录则显示警告并返回None"""
    if not st.session_state.get("logged_in"):
        st.warning("请先登录")
        return False
    return True
