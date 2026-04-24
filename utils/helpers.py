"""
通用辅助函数
"""
from .constants import VO2MAX_LEVELS, LEVEL_BG_COLORS


def get_age_group(age: int) -> str:
    """根据年龄返回年龄分组"""
    if 20 <= age <= 29: return "20-29岁"
    if 30 <= age <= 39: return "30-39岁"
    if 40 <= age <= 49: return "40-49岁"
    if 50 <= age <= 59: return "50-59岁"
    if 60 <= age <= 69: return "60-69岁"
    return "20-29岁"  # 默认值


def get_vo2max_level(sex: str, age: int, vo2max_value: float) -> str:
    """根据性别、年龄和VO₂max值，返回健康评级"""
    age_group = get_age_group(age)
    if sex not in VO2MAX_LEVELS:
        return "无法评估"

    thresholds = VO2MAX_LEVELS[sex].get(age_group)
    if not thresholds:
        return "无法评估"

    if vo2max_value >= thresholds["出色"]: return "出色"
    if vo2max_value >= thresholds["优秀"]: return "优秀"
    if vo2max_value >= thresholds["良好"]: return "良好"
    if vo2max_value >= thresholds["一般"]: return "一般"
    if vo2max_value >= thresholds["差"]: return "差"
    return "极差"


def get_percentile_and_segment(sex: str, age: int, vo2max: float):
    """计算百分位数和等级"""
    age_group = get_age_group(age)
    thresholds = VO2MAX_LEVELS[sex][age_group]
    levels = ["极差", "差", "一般", "良好", "优秀", "出色"]
    values = [thresholds["差"], thresholds["一般"], thresholds["良好"], thresholds["优秀"], thresholds["出色"]]

    if vo2max < values[0]:
        return 0, "极差"
    if vo2max >= values[-1]:
        return 100, "出色"

    for i in range(1, len(values)):
        if vo2max < values[i]:
            seg_start = values[i-1]
            seg_end = values[i]
            percent = 20 * i + 20 * (vo2max - seg_start) / (seg_end - seg_start)
            return int(percent), levels[i]
    return 100, "出色"


def format_table_with_ranges(gender_data):
    """将下限值数据转换为范围区间的DataFrame"""
    import pandas as pd
    levels_ordered = ["出色", "优秀", "良好", "一般", "差", "极差"]
    display_data = {}

    for age_group, thresholds in gender_data.items():
        display_data[age_group] = {}
        sorted_thresholds = sorted(thresholds.items(), key=lambda item: item[1], reverse=True)

        for i, (level, lower_bound) in enumerate(sorted_thresholds):
            if i == 0:
                range_str = f"≥ {lower_bound:.1f}"
            else:
                upper_bound = sorted_thresholds[i-1][1]
                range_str = f"{lower_bound:.1f} - {upper_bound - 0.1:.1f}"
            display_data[age_group][level] = range_str

        last_level_lower_bound = sorted_thresholds[-1][1]
        display_data[age_group]["极差"] = f"< {last_level_lower_bound:.1f}"

    df = pd.DataFrame(display_data)
    df = df.reindex(levels_ordered)
    df.index.name = "评级"
    return df