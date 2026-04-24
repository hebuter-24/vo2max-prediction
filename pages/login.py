"""
登录与注册页面
"""
import streamlit as st
from utils.auth import login, register, logout, init_session_state

# 初始化 session state
init_session_state()

# 页面配置
st.set_page_config(page_title="登录 - VO₂max 预测系统", page_icon="🔐", layout="centered")


def render_login_register():
    """渲染登录/注册页面"""
    st.title("🔐 登录 / 注册")

    # 如果已登录，显示用户信息
    if st.session_state.get("logged_in"):
        st.success(f"当前登录用户: {st.session_state.username}")
        if st.button("退出登录"):
            logout()
            st.rerun()
        return

    # Tab 切换
    tab1, tab2 = st.tabs(["登录", "注册"])

    with tab1:
        st.subheader("用户登录")
        login_username = st.text_input("用户名", key="login_username")
        login_password = st.text_input("密码", type="password", key="login_password")

        if st.button("登录", type="primary", width="stretch"):
            if login_username and login_password:
                if login(login_username, login_password):
                    st.success("登录成功！")
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
            else:
                st.warning("请填写用户名和密码")

    with tab2:
        st.subheader("新用户注册")
        reg_username = st.text_input("用户名", key="reg_username")
        reg_password = st.text_input("密码", type="password", key="reg_password")
        reg_password2 = st.text_input("确认密码", type="password", key="reg_password2")

        if st.button("注册", type="primary", width="stretch"):
            if reg_username and reg_password and reg_password2:
                if reg_password != reg_password2:
                    st.error("两次输入的密码不一致")
                else:
                    success, message = register(reg_username, reg_password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.warning("请填写所有字段")

    st.markdown("---")
    st.markdown("💡 提示：注册后即可使用预测功能，所有历史记录将与您的账号关联。")


if __name__ == "__main__":
    render_login_register()