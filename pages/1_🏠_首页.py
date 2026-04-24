"""
首页 - 系统介绍
"""
import streamlit as st

st.set_page_config(page_title="VO₂max 预测系统", page_icon="🏃‍♂️", layout="wide")


def render_home():
    """渲染首页"""
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

    st.info("👈 请使用左侧导航菜单切换功能。首次使用请先登录或注册账号。")

    # 系统说明
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
    render_home()
