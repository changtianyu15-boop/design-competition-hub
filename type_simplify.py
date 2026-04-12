"""与 static/index.html 中 simpleCompetitionType() 规则保持一致，供导出等后端逻辑使用。"""

from __future__ import annotations


def simple_competition_type(raw: str | None) -> str:
    s = (raw or "").strip()
    if not s or s == "未分类":
        return "其他"
    lower = s.lower()

    rules: list[tuple[str, tuple[str, ...]]] = [
        (
            "创新创业",
            (
                "创新",
                "创业",
                "创客",
                "挑战杯",
                "互联网+",
                "互联网＋",
                "服务外包",
                "三创",
                "外包",
                "红旅",
                "创青春",
            ),
        ),
        (
            "数字媒体",
            (
                "数字",
                "交互",
                "ui",
                "ux",
                "界面",
                "动画",
                "游戏",
                "数媒",
                "影像",
                "摄影",
                "可视化",
                "智能车",
                "软件",
                "移动应用",
                "服务设计",
                "用户体验",
                "智慧城市",
                "swift",
                "bim",
                "信息可视化",
            ),
        ),
        (
            "空间环境",
            (
                "室内",
                "建筑",
                "景观",
                "园林",
                "环艺",
                "城乡",
                "乡村",
                "文旅",
                "人居",
                "城市规划",
                "城市设计",
                "更新",
                "照明",
                "雕塑",
                "公共艺术",
                "绿色建筑",
                "展陈",
                "空间",
                "环境设计",
            ),
        ),
        (
            "产品与工业",
            (
                "产品",
                "工业",
                "概念",
                "cmf",
                "家居",
                "家具",
                "汽车",
                "交通",
                "珠宝",
                "时装",
                "服装",
                "时尚",
                "穿戴",
                "装备",
                "机械",
                "可持续",
                "交通工具",
            ),
        ),
        (
            "平面设计",
            (
                "平面",
                "视觉",
                "品牌",
                "传达",
                "包装",
                "字体",
                "广告",
                "插画",
                "绘本",
                "图形",
                "文创",
                "漫画",
                "标志",
            ),
        ),
    ]

    for name, keys in rules:
        if any(k in s or k in lower for k in keys):
            return name
    if "综合" in s or "多学科" in s:
        return "综合"
    return "其他"
