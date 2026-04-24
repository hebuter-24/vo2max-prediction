"""
健康档案页面 - 展示用户历史预测记录
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.auth import require_login, get_current_user
from database.crud import get_user_predictions, get_user_prediction_stats

st.set_page_config(page_title="健康档案 - VO₂max 预测系统", page_icon="📋", layout="wide")


def render_health_profile():
    """渲染健康档案页面"""
    if not require_login():
        st.warning("请先登录以查看健康档案")
        return

    user = get_current_user()
    st.title(f"📋 {user.username} 的健康档案")

    # 获取统计信息
    stats = get_user_prediction_stats(user.id)

    # 显示统计卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总预测次数", stats["total"])
    with col2:
        st.metric("平均 VO₂max", f"{stats['avg_vo2max']} mL/kg/min")
    with col3:
        st.metric("最高 VO₂max", f"{stats['max_vo2max']} mL/kg/min")
    with col4:
        st.metric("最低 VO₂max", f"{stats['min_vo2max']} mL/kg/min")

    st.markdown("---")

    # 获取所有预测记录
    records = get_user_predictions(user.id)

    if not records:
        st.info("您还没有任何预测记录。请前往心肺预测页面开始预测。")
        return

    # 转换为 DataFrame
    data = []
    for r in records:
        data.append({
            "ID": r.id,
            "日期": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "",
            "年龄": r.age,
            "性别": r.sex,
            "身高 (cm)": r.height,
            "体重 (kg)": r.weight,
            "静息心率": r.rest_hr,
            "最大心率": r.max_hr,
            "VO₂max 值": f"{r.vo2max:.1f}",
            "百分位": f"{r.percentile}%",
            "等级": r.level,
        })

    df = pd.DataFrame(data)

    st.subheader("📊 历史预测记录")
    st.dataframe(df, width="stretch", hide_index=True)

    # 详细查看某次记录
    with st.expander("查看详细方案（点击展开）"):
        record_id = st.selectbox("选择记录 ID", options=[r.id for r in records], format_func=lambda x: f"ID: {x}")
        selected = next((r for r in records if r.id == record_id), None)
        if selected:
            st.markdown(selected.plan_html, unsafe_allow_html=True)


if __name__ == "__main__":
    render_health_profile()