"""
VO₂max 预测系统 - 主入口
Streamlit 多页面应用
"""
import streamlit as st

# 初始化数据库
from database.init_db import init_database
init_database()

# 初始化 session state
from utils.auth import init_session_state, logout, get_current_user
init_session_state()

# 页面配置
st.set_page_config(
    page_title="VO₂max 智能预测系统",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 侧边栏导航
st.markdown("""
<style>
    /* 隐藏默认 Streamlit 侧边栏 */
    [data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)


def main():
    """主函数"""
    # 侧边栏 - 用户状态
    with st.sidebar:
        st.markdown("### 🏃 VO₂max 预测系统")
        st.markdown("---")

        # 用户状态
        if st.session_state.get("logged_in"):
            st.success(f"✅ {st.session_state.username}")
            if st.button("退出登录", width="stretch"):
                logout()
                st.rerun()
        else:
            st.info("👤 未登录")
            if st.button("登录 / 注册", width="stretch", type="primary"):
                st.switch_page("pages/login.py")

        st.markdown("---")

        # 导航菜单
        st.markdown("### 📌 功能导航")
        menu_options = {
            "🏠 首页": "pages/1_🏠_首页.py",
            "🏃 心肺预测": "pages/2_🏃_心肺预测.py",
            "📋 健康档案": "pages/3_📋_健康档案.py",
            "📈 数据分析": "pages/4_📈_数据分析.py",
        }

        for label, page_path in menu_options.items():
            if st.button(f"  {label}", width="stretch"):
                st.switch_page(page_path)

        st.markdown("---")

        # 底部信息
        st.markdown("""
        <div style="position: fixed; bottom: 10px; font-size: 12px; color: #888;">
            © 2025 VO₂max 预测系统<br>
            基于 XGBoost 机器学习
        </div>
        """, unsafe_allow_html=True)

    # 主内容区 - 根据 session_state 显示不同页面
    if "page" not in st.session_state:
        st.session_state.page = "home"

    # 渲染首页（默认）
    st.title("🏃‍♂️ VO₂max 智能预测与运动处方系统")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 🔬 精准预测
        基于 XGBoost 机器学习算法，使用年龄、性别、生理指标等数据，精准预测您的心肺耐力水平。
        """)

    with col2:
        st.markdown("""
        ### 📊 科学评估
        参照 ACSM（美国运动医学会）标准，根据您的 VO₂max 值给出科学的健康评级。
        """)

    with col3:
        st.markdown("""
        ### 🏋️ 个性化方案
        基于 FITT-VP 原则，自动生成符合您身体状况的运动训练处方。
        """)

    st.markdown("---")

    st.markdown("""
    ## 系统功能

    | 功能 | 说明 |
    |------|------|
    | 🏃 心肺预测 | 输入生理数据，预测您的最大摄氧量 (VO₂max) |
    | 📋 健康档案 | 查看您所有的历史预测记录 |
    | 📈 数据分析 | 可视化您的健康数据变化趋势 |

    ---
    """)

    # 快速入口按钮
    st.markdown("### 🚀 快速入口")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🏠 首页", width="stretch"):
            st.switch_page("pages/1_🏠_首页.py")

    with col2:
        if st.button("🏃 心肺预测", width="stretch"):
            st.switch_page("pages/2_🏃_心肺预测.py")

    with col3:
        if st.button("📋 健康档案", width="stretch"):
            st.switch_page("pages/3_📋_健康档案.py")

    with col4:
        if st.button("📈 数据分析", width="stretch"):
            st.switch_page("pages/4_📈_数据分析.py")

    st.markdown("---")
    st.info("👈 请使用左侧导航菜单或上方快速入口切换功能。首次使用请先登录或注册账号。")

    # 关于 VO₂max
    with st.expander("ℹ️ 关于 VO₂max"):
        st.markdown("""
        **什么是 VO₂max？**

        最大摄氧量（VO₂max）是指在进行剧烈运动时，人体每公斤体重每分钟能消耗的氧气量（mL/kg/min）。

        它是衡量心肺适能的最重要指标，也被称为"第五大生命体征"。

        **VO₂max 与健康的关系：**

        - VO₂max 越高，表示心肺功能越好
        - 较高的 VO₂max 与较低的心血管疾病风险相关
        - 通过规律运动可以有效提高 VO₂max
        """)


if __name__ == "__main__":
    main()