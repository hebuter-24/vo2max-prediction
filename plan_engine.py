from typing import Tuple, List, Optional
from dataclasses import dataclass
import os


def estimate_hr_max(age: int) -> int:
    """估算最大心率。当用户未提供时采用 220 - 年龄。"""
    return 220 - int(age)


def compute_target_hr_range(rest_hr: int, max_hr: int, low_pct: float, high_pct: float) -> Tuple[int, int]:
    """基于HRR(≈VO₂R)计算目标心率区间。pct输入为0-1。"""
    heart_rate_reserve = max_hr - rest_hr
    low = int(round(rest_hr + heart_rate_reserve * low_pct))
    high = int(round(rest_hr + heart_rate_reserve * high_pct))
    return low, high


def get_fitt_rules(level: str, age: int):
    """根据ACSM建议并结合当前等级给出规则参数。返回频率、强度百分比、时长、类型建议。"""
    # 安全映射表：包含全部 6 个等级，使用 .get() 安全访问
    level_to_pct = {
        "极差": (0.40, 0.55),
        "差": (0.40, 0.59),
        "一般": (0.50, 0.69),
        "良好": (0.60, 0.74),
        "优秀": (0.70, 0.85),
        "出色": (0.75, 0.90),
    }
    level_to_freq_time = {
        "极差": ((3, 4), (20, 30)),
        "差": ((3, 4), (25, 40)),
        "一般": ((3, 5), (30, 45)),
        "良好": ((4, 5), (40, 60)),
        "优秀": ((4, 5), (45, 60)),
        "出色": ((4, 6), (45, 75)),
    }
    level_to_suggestions = {
        "极差": ["快走", "骑行(低阻力)", "水中有氧", "椭圆机"],
        "差": ["快走", "骑行(低阻力)", "水中有氧", "椭圆机"],
        "一般": ["骑行", "快走", "慢跑", "游泳", "椭圆机", "踏步机", "划船机"],
        "良好": ["骑行", "快走", "慢跑", "游泳", "椭圆机", "踏步机", "划船机"],
        "优秀": ["慢跑/跑步", "间歇骑行", "游泳", "爬坡徒步", "划船机"],
        "出色": ["慢跑/跑步", "间歇骑行", "游泳", "爬坡徒步", "划船机"],
    }

    # 确保等级合法（安全回退）
    valid_levels = list(level_to_pct.keys())
    if level not in valid_levels:
        level = "一般"  # 默认回退

    # 获取各参数（使用 .get() 确保安全）
    base_pct = level_to_pct.get(level, (0.50, 0.69))
    base_freq, base_time = level_to_freq_time.get(level, ((3, 5), (30, 45)))
    types = level_to_suggestions.get(level, ["骑行", "快走", "慢跑", "游泳"])

    # 年龄 >= 60 适当降低强度
    if age >= 60:
        pct_range = (max(0.35, base_pct[0] - 0.05), max(0.55, base_pct[1] - 0.05))
    else:
        pct_range = base_pct

    return base_freq, pct_range, base_time, types


def build_plan_html(freq_range, hr_low, hr_high, time_range, types, weekly_minutes) -> str:
    """生成接近“图二”风格的处方卡片HTML，使用表格布局避免被转义。"""
    types_str = "、".join(types)
    freq_text = f"每周{freq_range[0]}~{freq_range[1]}次"
    inten_text = f"心率：{hr_low}-{hr_high}次/分；超过{hr_high}次/分请控制在3-5分钟以内"
    time_text = f"每次{time_range[0]}-{time_range[1]}分钟"

    html = f"""
    <div style='margin-top:16px;'>
      <div style='background:#64aeb0; color:#fff; border-radius:12px 12px 0 0; padding:14px 0; text-align:center; font-size:24px; font-weight:700;'>
        您的心肺耐力训练方案
      </div>
      <div style='background:#e6f1f1; border-radius:0 0 12px 12px; padding:0 0 8px 0; color:#5a7c7d;'>
        <table style='width:100%; border-collapse:separate; border-spacing:0; font-size:20px;'>
          <tr>
            <td style='width:260px; padding:24px 24px; font-weight:700;'>F- frequency 频率</td>
            <td style='padding:24px 24px;'>{freq_text}</td>
          </tr>
          <tr>
            <td style='width:260px; padding:24px 24px; font-weight:700; border-top:1px solid #c9dddd;'>I- 心率</td>
            <td style='padding:24px 24px; border-top:1px solid #c9dddd;'>{inten_text}</td>
          </tr>
          <tr>
            <td style='width:260px; padding:24px 24px; font-weight:700; border-top:1px solid #c9dddd;'>T- time 时间</td>
            <td style='padding:24px 24px; border-top:1px solid #c9dddd;'>{time_text}</td>
          </tr>
          <tr>
            <td style='width:260px; padding:24px 24px; font-weight:700; border-top:1px solid #c9dddd;'>T- type 类型</td>
            <td style='padding:24px 24px; border-top:1px solid #c9dddd;'>持续性的、有节奏的、动员大肌群的运动，如{types_str} 等（以达到目标心率为准）</td>
          </tr>
        </table>
      </div>
    </div>
    <div style='margin-top:18px; color:#6b7d7e;'>
      <div style='font-size:18px; font-weight:700; margin-bottom:8px;'>方案执行说明</div>
      <div style='font-size:16px; line-height:1.9;'>
        <div>⚠️ 本方案依据美国运动医学会（ACSM）指南，并结合您的个体数据自动生成。</div>
        <div>⚠️ 注意运动前后一般需5分钟左右的热身和冷却时间。</div>
        <div>⚠️ 方案根据您当次的运动测试制定；如既往缺乏规律运动训练，建议在复测前不要盲目增加强度以避免运动损伤；为确保方案安全有效，建议每三个月复测一次以调整处方。</div>
      </div>
    </div>
    """
    return html


def generate_fitt_plan(age: int, rest_hr: int, max_hr: int, level: str) -> str:
    """对外主函数：输入年龄、静息/最大心率与VO₂max等级，输出可直接渲染的HTML。"""
    if not max_hr or max_hr <= 0:
        max_hr = estimate_hr_max(age)

    freq_range, pct_range, time_range, types = get_fitt_rules(level, age)
    hr_low, hr_high = compute_target_hr_range(rest_hr, max_hr, pct_range[0], pct_range[1])
    weekly_minutes = int(round(((time_range[0] + time_range[1]) / 2.0) * ((freq_range[0] + freq_range[1]) / 2.0)))
    return build_plan_html(freq_range, hr_low, hr_high, time_range, types, weekly_minutes)


def generate_personalized_plan(sex: str, age: int, height_cm: float, weight_kg: float, rest_hr: int, max_hr: int, vo2max: float, level: str) -> str:
    """统一对外接口：优先使用RL结果，失败则回退规则库。
    返回HTML字符串，直接在前端渲染。
    """
    # 兜底最大心率
    if not max_hr or max_hr <= 0:
        max_hr = estimate_hr_max(age)

    try:
        # 0) 优先尝试 PPO 推理（如安装并提供模型）
        ppo_plan = recommend_plan_ppo_optional(
            sex=sex,
            age=age,
            height_cm=height_cm,
            weight_kg=weight_kg,
            rest_hr=rest_hr,
            max_hr=max_hr,
            vo2max=vo2max,
        )
        if ppo_plan is not None:
            hr_low, hr_high = compute_target_hr_range(int(rest_hr), int(max_hr), ppo_plan['pct_range'][0], ppo_plan['pct_range'][1])
            weekly_minutes = int(((ppo_plan['time_range'][0] + ppo_plan['time_range'][1]) / 2.0) * ((ppo_plan['freq_range'][0] + ppo_plan['freq_range'][1]) / 2.0))
            return build_plan_html(ppo_plan['freq_range'], hr_low, hr_high, ppo_plan['time_range'], ppo_plan['types'], weekly_minutes)

        # 1) 内置RL占位：给出频率/强度/时间/类型
        bmi_val = float(weight_kg) / ((float(height_cm) / 100.0) ** 2) if height_cm and height_cm > 0 else 0.0
        state = RLState(
            sex=sex,
            age=int(age),
            height_cm=float(height_cm),
            weight_kg=float(weight_kg),
            bmi=bmi_val,
            hr_rest=int(rest_hr),
            hr_max=int(max_hr),
            vo2max=float(vo2max),
        )
        rl_plan = recommend_plan_rl(state)

        # 2) 将百分比映射为目标心率区间并渲染
        hr_low, hr_high = compute_target_hr_range(int(rest_hr), int(max_hr), rl_plan['pct_range'][0], rl_plan['pct_range'][1])
        weekly_minutes = int(((rl_plan['time_range'][0] + rl_plan['time_range'][1]) / 2.0) * ((rl_plan['freq_range'][0] + rl_plan['freq_range'][1]) / 2.0))
        return build_plan_html(rl_plan['freq_range'], hr_low, hr_high, rl_plan['time_range'], rl_plan['types'], weekly_minutes)
    except Exception:
        # 回退：基于规则库与等级生成
        return generate_fitt_plan(age=age, rest_hr=rest_hr, max_hr=max_hr, level=level)


# ================== 内置 RL 引擎占位实现 ==================
@dataclass
class RLState:
    sex: str
    age: int
    height_cm: float
    weight_kg: float
    bmi: float
    hr_rest: int
    hr_max: int
    vo2max: float
    adherence: float = 1.0
    rpe: float = 3.0
    hrr_1min: float = 15.0


def recommend_plan_rl(state: RLState):
    """占位实现：根据VO₂max粗略映射输出处方参数。"""
    if state.vo2max >= 55:
        pct = (0.75, 0.9)
        freq = (4, 6)
        minutes = (45, 60)
        types = ["慢跑/跑步", "间歇骑行", "游泳", "爬坡徒步", "划船机"]
    elif state.vo2max >= 45:
        pct = (0.6, 0.75)
        freq = (4, 5)
        minutes = (40, 60)
        types = ["慢跑", "骑行", "游泳", "椭圆机"]
    elif state.vo2max >= 35:
        pct = (0.5, 0.69)
        freq = (3, 5)
        minutes = (30, 45)
        types = ["快走", "骑行", "椭圆机", "水中有氧"]
    else:
        pct = (0.4, 0.55)
        freq = (3, 4)
        minutes = (20, 30)
        types = ["快走", "骑行(低阻力)", "水中有氧", "椭圆机"]

    return {
        "pct_range": pct,
        "freq_range": freq,
        "time_range": minutes,
        "types": types,
    }


# ================== 可选 PPO 推理 ==================
_PPO_MODEL_CACHE = None


def _load_ppo_model(model_path: str):
    global _PPO_MODEL_CACHE
    if _PPO_MODEL_CACHE is not None:
        return _PPO_MODEL_CACHE
    try:
        from stable_baselines3 import PPO  # type: ignore
        if os.path.exists(model_path):
            _PPO_MODEL_CACHE = PPO.load(model_path)
            return _PPO_MODEL_CACHE
        return None
    except Exception:
        return None


def _build_state_vector(sex: str, age: int, height_cm: float, weight_kg: float, rest_hr: int, max_hr: int, vo2max: float):
    bmi_val = float(weight_kg) / ((float(height_cm) / 100.0) ** 2) if height_cm and height_cm > 0 else 0.0
    sex_num = 1.0 if sex == "男" else 0.0
    # 归一化到大致范围，防止模型期望的尺度差异（示例）
    return [
        sex_num,
        age / 100.0,
        height_cm / 220.0,
        weight_kg / 150.0,
        bmi_val / 45.0,
        rest_hr / 200.0,
        max_hr / 220.0,
        vo2max / 80.0,
    ]


def _get_base_path():
    """获取项目根目录的绝对路径（兼容打包环境）"""
    import sys as _sys
    if getattr(_sys, 'frozen', False) and hasattr(_sys, '_MEIPASS'):
        return Path(os.path.abspath(os.path.dirname(_sys.executable)))
    return Path(os.path.abspath(os.path.dirname(__file__)))


def recommend_plan_ppo_optional(sex: str, age: int, height_cm: float, weight_kg: float, rest_hr: int, max_hr: int, vo2max: float, model_path: Optional[str] = None):
    """如可用，使用PPO模型进行推理，返回与RL同结构的处方；不可用则返回None。"""
    if model_path is None:
        model_path = os.getenv("PPO_PLAN_MODEL", str(_get_base_path() / "ppo_plan_model.zip"))

    model = _load_ppo_model(model_path)
    if model is None:
        return None

    obs = _build_state_vector(sex, age, height_cm, weight_kg, rest_hr, max_hr, vo2max)
    try:
        import numpy as np  # type: ignore
        action, _ = model.predict(np.array(obs), deterministic=True)
        a = np.clip(action, 0.0, 1.0)
        low_pct = 0.4 + 0.5 * float(a[0])
        high_pct = max(low_pct + 0.05, 0.5 + 0.4 * float(a[1]))
        t_min, t_max = 20, 75
        t_len = int(round(t_min + (t_max - t_min) * float(a[2])))
        f_min, f_max = 3, 6
        f_cnt = int(round(f_min + (f_max - f_min) * float(a[3])))
        types = ["快走", "骑行", "慢跑", "游泳", "椭圆机", "划船机"]
        if high_pct >= 0.75:
            types = ["慢跑/跑步", "间歇骑行", "游泳", "爬坡徒步", "划船机"]
        elif low_pct <= 0.5:
            types = ["快走", "骑行(低阻力)", "水中有氧", "椭圆机"]

        return {
            "pct_range": (float(low_pct), float(high_pct)),
            "freq_range": (max(3, f_cnt - 1), min(6, f_cnt + 1)),
            "time_range": (max(20, t_len - 5), min(75, t_len + 5)),
            "types": types,
        }
    except Exception:
        return None

