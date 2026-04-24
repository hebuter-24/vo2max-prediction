"""
共享 UI 组件
"""
import streamlit as st


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
    """渲染分段进度条（大版）"""
    seg_colors = ["#888", "#aaa", "#ddd", "#90caf9", "#1976d2"]
    seg_labels = ["极差", "差", "一般", "优秀", "出色"]
    html = f'''
    <div style="width: 100%; display: flex; flex-direction: column; align-items: center;">
      <div style="font-weight: bold; text-align: center; color: #666; margin-bottom: 16px; font-size:16px; width: 100%;">
        你的心肺适能与他人（同性别/年龄）相比如何
      </div>
      <div style="width: 98%;">
        <div style="display: flex; height: 36px; border-radius: 18px; overflow: hidden;">
          {''.join([f'<div style="flex:1; background:{c};"></div>' for c in seg_colors])}
        </div>
        <div style="position: relative; margin-top: -42px; height: 0;">
          <div style="position: absolute; left: {percent}%; transform: translateX(-50%); background: #fff; border: 2px solid #888; border-radius: 24px; padding: 4px 20px; font-size: 22px; color: #1976d2;">
            {percent}%
          </div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 22px; color: #444; font-size:16px; letter-spacing: 1px;">
          {''.join([f'<span style="flex:1; text-align:center;">{l}</span>' for l in seg_labels])}
        </div>
      </div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def style_dataframe(df):
    """为DataFrame添加背景色样式"""
    def get_row_style(row):
        from utils.constants import LEVEL_BG_COLORS
        color = LEVEL_BG_COLORS.get(row.name, "")
        if color:
            return [f'background-color: {color}' for _ in row]
        return ['' for _ in row]
    return df.style.apply(get_row_style, axis=1)
