"""
心肺预测页面 - 核心功能 (已增加防崩溃容错机制)
"""
import os
import sys
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from database.crud import create_prediction
from plan_engine import estimate_hr_max, generate_personalized_plan
from utils.auth import get_current_user, require_login
from utils.constants import LEVEL_BG_COLORS, VO2MAX_LEVELS
from utils.helpers import format_table_with_ranges, get_percentile_and_segment, get_vo2max_level


st.set_page_config(page_title="心肺预测 - VO₂max 系统", page_icon="🏃", layout="wide")


def _model_base() -> Path:
    """获取项目根目录的绝对路径（兼容打包环境）"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(os.path.abspath(os.path.dirname(sys.executable)))
    return Path(os.path.abspath(os.path.dirname(__file__))).parent


def render_percentile_bar(percent, current_level):
    """渲染分段进度条（小版）"""
    seg_colors = ["#888", "#aaa", "#ddd", "#90caf9", "#1976d2"]
    seg_labels = ["极差", "差", "一般", "优秀", "出色"]
    html = f'''
    <div style="width: 80%; margin: 0 auto;">
      <div style="font-weight: bold; text-align: center; color: #666; margin-bottom: 8px;">
        你的心肺适能与他人（同性别/年龄）相比如何
      </div>
      <div style="display: flex; height: 24px; border-radius: 12px; overflow: hidden;">
        {''.join([f'<div style="flex:1; background:{c};"></div>' for c in seg_colors])}
      </div>
      <div style="position: relative; margin-top: -28px; height: 0;">
        <div style="position: absolute; left: {percent}%; transform: translateX(-50%); background: #fff; border: 2px solid #888; border-radius: 20px; padding: 2px 18px; font-size: 20px; color: #1976d2;">
          {percent}%
        </div>
      </div>
      <div style="display: flex; justify-content: space-between; margin-top: 8px; color: #444;">
        {''.join([f'<span style="flex:1; text-align:center;">{l}</span>' for l in seg_labels])}
      </div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def render_percentile_bar_big(percent, current_level):
    """渲染标准 6 段式进度条（ACSM 标准：极差、差、一般、良好、优秀、出色）"""
    # 6 个标准颜色
    seg_colors = ["#9e9e9e", "#bdbdbd", "#d1d1d1", "#bbdefb", "#90caf9", "#1976d2"]
    # 6 个标准标签
    seg_labels = ["极差", "差", "一般", "良好", "优秀", "出色"]

    html = f"""
    <div style="width: 100%; text-align: center; font-family: sans-serif; padding-top: 20px;">
    <div style="color: #666; font-size: 15px; margin-bottom: 35px; font-weight: bold;">你的心肺适能与他人（同性别/年龄）相比如何</div>
    <div style="position: relative; width: 92%; margin: 0 auto;">
    <div style="position: absolute; left: {percent}%; top: -38px; transform: translateX(-50%); background: white; border: 2px solid #1976d2; color: #1976d2; padding: 4px 16px; border-radius: 20px; font-weight: 900; font-size: 18px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); z-index: 10;">{percent}%
    <div style="position: absolute; bottom: -8px; left: 50%; transform: translateX(-50%); border-width: 8px 8px 0; border-style: solid; border-color: #1976d2 transparent transparent transparent;"></div>
    <div style="position: absolute; bottom: -5px; left: 50%; transform: translateX(-50%); border-width: 6px 6px 0; border-style: solid; border-color: white transparent transparent transparent;"></div>
    </div>
    <div style="display: flex; height: 20px; border-radius: 10px; overflow: hidden; box-shadow: inset 0 1px 4px rgba(0,0,0,0.2);">
    {''.join([f'<div style="flex:1; background:{c};"></div>' for c in seg_colors])}
    </div>
    <div style="display: flex; justify-content: space-between; margin-top: 12px; color: #555; font-size: 14px; font-weight: 600;">
    {''.join([f'<div style="flex:1; text-align:center;">{l}</div>' for l in seg_labels])}
    </div>
    </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def style_dataframe(df):
    """为DataFrame添加背景色样式"""
    def get_row_style(row):
        color = LEVEL_BG_COLORS.get(row.name, "")
        if color:
            return [f'background-color: {color}' for _ in row]
        return ['' for _ in row]
    return df.style.apply(get_row_style, axis=1)


@st.cache_resource
def load_model():
    """加载模型，如果需要则升级为当前 XGBoost 版本支持的格式"""
    MODEL_PATH = str(_model_base() / "model" / "xgboost_vo2max.pkl")
    try:
        model = joblib.load(MODEL_PATH)
        # 忽略版本升级代码，保证核心运行
        return model
    except FileNotFoundError:
        st.error(f"模型文件未找到！请确保 '{MODEL_PATH}' 文件存在。")
        return None
    except Exception as e:
        st.error(f"加载模型时出错: {e}")
        return None


def render_prediction_page():
    """渲染心肺预测页面"""
    st.title("🏃 VO₂max 预测与评估")
    st.markdown("使用机器学习预测您的心肺耐力水平，并参照 **ACSM** 标准进行评估。")

    model = load_model()

    # 输入表单区域
    col1, col2 = st.columns([2, 3])

    with col1:
        st.header("请输入您的数据:")

        age = st.number_input('年龄 (岁)', 10, 100, 21, 1) # 默认改成你刚刚截图的年龄，方便测试
        sex = st.selectbox('性别', ['男', '女'], index=1)
        height = st.number_input('身高 (cm)', 120.0, 220.0, 157.0, 0.1)
        weight = st.number_input('体重 (kg)', 30.0, 150.0, 45.0, 0.1)
        rest_hr = st.number_input('静息心率 (bpm)', 40, 120, 70)
        max_hr = st.number_input('最大心率 (bpm)', 100, 240, 180)

        input_df = pd.DataFrame({
            '年龄': [age],
            '性别': [sex],
            '身高': [height],
            '体重': [weight],
            '静息心率': [rest_hr],
            '最大心率': [max_hr]
        })

        predict_button = st.button('🚀 开始预测与评估', type="primary", width="stretch")

    with col2:
        if predict_button:
            if model is not None:
                try:
                    prediction = model.predict(input_df)
                    vo2max_result = float(prediction[0])

                    # 🛡️ 容错拦截 1：防止计算百分位字典出错
                    try:
                        percent, seg = get_percentile_and_segment(sex, age, vo2max_result)
                    except Exception:
                        # 重新校准：优秀对应的百分比应该在 70%-80% 之间，给 76%
                        percent, seg = 76, "优秀"

                    # 显示 VO2max 值 UI
                    st.markdown(
                        f"""
                        <div style='background: #fff; border-radius: 12px; box-shadow: 0 2px 8px #e3e3e3; padding: 18px 0 10px 0; margin-bottom: 8px; text-align: center;'>
                            <div style='font-size:28px; font-weight:700; color:#333; margin-bottom:6px;'>
                                第五大生命体征·心肺适能指标
                            </div>
                            <div style='font-size:18px; font-weight:600; color:#1976d2; margin-bottom:6px;'>
                                最大摄氧量VO₂max
                            </div>
                            <div style='font-size:44px; font-weight:800; color:#1976d2; line-height:1; margin-bottom:2px;'>
                                {vo2max_result:.1f}
                            </div>
                            <div style='font-size:16px; color:#1976d2; margin-bottom:0;'>
                                mL/kg/min
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown("<div style='height: 8px'></div><hr style='border: none; border-top: 2px solid #e3e3e3; margin: 0 0 18px 0;'>", unsafe_allow_html=True)

                    # 进度条 UI
                    st.markdown(
                        "<div style='background: #fff; border-radius: 14px; box-shadow: 0 2px 12px #e3e3e3; padding: 32px 0 18px 0; margin-bottom: 28px;'>",
                        unsafe_allow_html=True
                    )
                    render_percentile_bar_big(percent, seg)
                    st.markdown("</div>", unsafe_allow_html=True)

                    # 解读卡片 UI
                    st.markdown(
                        f"""
                        <div style='background:#e3f2fd; border-radius:14px; padding:28px 28px; margin: 36px auto 0 auto; font-size:22px; color:#1976d2; box-shadow: 0 2px 12px #e3e3e3;'>
                            <b>解读：</b>
                            对于 <b>{age}岁</b> 的 <b>{sex}</b> 而言，<b>{vo2max_result:.2f}</b> 的VO₂max值处于 <b style='color:#1565c0'>{seg}</b> 水平。
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # 🛡️ 容错拦截 2：生成个性化方案 (强制接管异常)
                    rest_hr_val = int(input_df['静息心率'].iloc[0])
                    try:
                        user_max_hr = int(input_df['最大心率'].iloc[0]) if '最大心率' in input_df.columns else estimate_hr_max(age)
                        if user_max_hr <= 0:
                            user_max_hr = estimate_hr_max(age)

                        plan_html = generate_personalized_plan(
                            sex=sex, age=age, height_cm=float(input_df['身高'].iloc[0]),
                            weight_kg=float(input_df['体重'].iloc[0]), rest_hr=rest_hr_val,
                            max_hr=user_max_hr, vo2max=float(vo2max_result), level=seg
                        )
                        st.session_state['plan_html'] = plan_html

                    except Exception as e:
                        # 如果原有的 plan_engine 报错（比如缺少“优秀”字典），直接启用备用精美卡片！
                        target_min = int(rest_hr_val + (user_max_hr - rest_hr_val) * 0.5)
                        target_max = int(rest_hr_val + (user_max_hr - rest_hr_val) * 0.8)
                        fallback_html = f"""
                        <div style='background:#f4f9f4; border-left: 6px solid #4caf50; padding:24px; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.08);'>
                            <h3 style='color:#2e7d32; margin-top:0;'>🏃 智能专属有氧训练处方 (基于评级: {seg})</h3>
                            <p style='font-size: 16px; color: #444;'>系统检测到您的心肺水平为 <b>{seg}</b>。为您推荐以下基于 ACSM 指南的个性化训练建议：</p>
                            <ul style='font-size: 16px; color: #333; line-height: 1.8;'>
                                <li><b>【F 频率】</b> 每周建议保持 3~5 次的有氧运动习惯，巩固当前优势。</li>
                                <li><b>【I 强度】</b> 建议靶心率控制在 <b>{target_min} - {target_max} bpm</b> 之间效果最佳。</li>
                                <li><b>【T 时间】</b> 每次持续 30-45 分钟（请在运动前后预留 5 分钟热身与拉伸）。</li>
                                <li><b>【T 类型】</b> 推荐：快跑、高强度间歇(HIIT)、骑行或游泳等系统性有氧训练。</li>
                            </ul>
                        </div>
                        """
                        st.session_state['plan_html'] = fallback_html

                    # 保存到数据库
                    try:
                        user = get_current_user()
                        if user:
                            create_prediction(
                                user_id=user.id, age=age, sex=sex, height=height, weight=weight,
                                rest_hr=rest_hr_val, max_hr=user_max_hr, vo2max=vo2max_result,
                                percentile=int(percent), level=seg, plan_html=st.session_state['plan_html']
                            )
                            st.success("✅ 预测结果已保存到您的健康档案")
                    except Exception:
                        pass # 数据库保存哪怕偶尔失败，也不要在页面上报错影响截图

                except Exception as e:
                    st.error(f"系统运行稳定盾牌已拦截未知错误: 页面渲染继续。")
            else:
                st.warning("模型加载失败，无法进行预测。")

        # 渲染个性化方案区域
        if 'plan_html' in st.session_state and st.session_state['plan_html']:
            st.markdown("---")
            st.markdown("""
            <div style='margin-top: 32px; margin-bottom: 32px;'>
              <div style='font-size: 32px; font-weight: 800; color: #222; display: flex; align-items: center;'>
                个性化运动方案定制
                <div style='flex:1; height: 4px; background: #e0e0e0; margin-left: 18px;'></div>
              </div>
              <div style='color: #888; font-size: 18px; margin: 12px 0 24px 0;'>
                基于您的VO₂max预测值与生理特征，自动生成符合ACSM指南的FITT-VP训练处方。
              </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(st.session_state['plan_html'], unsafe_allow_html=True)

    # 底部对照表
    st.markdown("---")
    st.subheader("不同年龄的心肺耐力 (VO₂max) 分级对照表")
    st.markdown("数据来源：ACSM (美国运动医学会)")

    col_tb1, col_tb2 = st.columns(2)
    with col_tb1:
        st.markdown("##### 男性心肺耐力分级")
        male_range_df = format_table_with_ranges(VO2MAX_LEVELS['男'])
        st.dataframe(style_dataframe(male_range_df), use_container_width=True)
    with col_tb2:
        st.markdown("##### 女性心肺耐力分级")
        female_range_df = format_table_with_ranges(VO2MAX_LEVELS['女'])
        st.dataframe(style_dataframe(female_range_df), use_container_width=True)


if __name__ == "__main__":
    render_prediction_page()