"""
数据分析页面 - 使用 Plotly 可视化用户历史数据
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.auth import require_login, get_current_user
from database.crud import get_user_predictions, get_user_prediction_stats

# Plotly 图表通用配置（隐藏工具栏，禁止缩放，避免警告）
PLOTLY_CONFIG = {
    "displayModeBar": False,
    "scrollZoom": False,
}


def render_data_analysis():
    """渲染数据分析页面"""
    if not require_login():
        st.warning("请先登录以查看数据分析")
        return

    user = get_current_user()
    st.title(f"📈 {user.username} 的数据分析")

    # 获取所有预测记录
    records = get_user_predictions(user.id)

    if not records:
        st.info("您还没有任何预测记录可供分析。请前往心肺预测页面开始预测。")
        return

    # 转换数据
    data = []
    for r in records:
        data.append({
            "id": r.id,
            "date": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "",
            "age": r.age,
            "sex": r.sex,
            "height": r.height,
            "weight": r.weight,
            "rest_hr": r.rest_hr,
            "max_hr": r.max_hr,
            "vo2max": r.vo2max,
            "percentile": r.percentile,
            "level": r.level,
        })

    df = pd.DataFrame(data)

    # 标签页
    tab1, tab2 = st.tabs(["📊 VO₂max 趋势", "📉 健康等级分布"])

    with tab1:
        st.subheader("VO₂max 预测趋势")

        # 折线图
        fig = px.line(
            df,
            x="date",
            y="vo2max",
            title="VO₂max 变化趋势",
            labels={"vo2max": "VO₂max (mL/kg/min)", "date": "预测日期"},
            markers=True,
        )
        fig.update_layout(
            height=400,
            template="plotly_white",
            xaxis_title="日期",
            yaxis_title="VO₂max (mL/kg/min)",
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

        # 百分位变化
        fig2 = px.area(
            df,
            x="date",
            y="percentile",
            title="百分位变化趋势",
            labels={"percentile": "百分位 (%)", "date": "预测日期"},
        )
        fig2.update_layout(height=300, template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True, config=PLOTLY_CONFIG)

    with tab2:
        st.subheader("健康等级分布")

        # 饼图 - 等级分布
        level_counts = df["level"].value_counts()
        fig_pie = px.pie(
            values=level_counts.values,
            names=level_counts.index,
            title="各等级次数分布",
            color=level_counts.index,
            color_discrete_map={
                "出色": "#FFF4E0",
                "优秀": "#E0F2F1",
                "良好": "#E3F2FD",
                "一般": "#F1F8E9",
                "差": "#FFEBEE",
                "极差": "#FFCDD2",
            }
        )
        fig_pie.update_layout(height=350)
        st.plotly_chart(fig_pie, use_container_width=True, config=PLOTLY_CONFIG)

        # 柱状图 - 各指标对比
        st.subheader("生理指标变化")
        col1, col2 = st.columns(2)

        with col1:
            # 静息心率趋势
            fig_hr = px.bar(
                df,
                x="date",
                y="rest_hr",
                title="静息心率变化",
                labels={"rest_hr": "静息心率 (bpm)", "date": "日期"},
            )
            fig_hr.update_layout(height=300, template="plotly_white")
            st.plotly_chart(fig_hr, use_container_width=True, config=PLOTLY_CONFIG)

        with col2:
            # 体重变化
            fig_weight = px.line(
                df,
                x="date",
                y="weight",
                title="体重变化",
                labels={"weight": "体重 (kg)", "date": "日期"},
                markers=True,
            )
            fig_weight.update_layout(height=300, template="plotly_white")
            st.plotly_chart(fig_weight, use_container_width=True, config=PLOTLY_CONFIG)

    # 数据统计表格
    st.markdown("---")
    st.subheader("📋 详细数据统计")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**VO₂max 统计**")
        stats_df = pd.DataFrame({
            "指标": ["平均值", "最大值", "最小值", "标准差"],
            "值": [
                f"{df['vo2max'].mean():.2f}",
                f"{df['vo2max'].max():.2f}",
                f"{df['vo2max'].min():.2f}",
                f"{df['vo2max'].std():.2f}",
            ]
        })
        st.dataframe(stats_df, hide_index=True, use_container_width=True)

    with col2:
        st.markdown("**百分位统计**")
        pct_df = pd.DataFrame({
            "指标": ["平均值", "最大值", "最小值"],
            "值": [
                f"{df['percentile'].mean():.1f}%",
                f"{df['percentile'].max():.1f}%",
                f"{df['percentile'].min():.1f}%",
            ]
        })
        st.dataframe(pct_df, hide_index=True, use_container_width=True)


if __name__ == "__main__":
    render_data_analysis()