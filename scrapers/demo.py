from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List

from models import Competition
from scrapers.base import Scraper


class DemoScraper(Scraper):
    """示例数据：网络不可用时仍可预览界面。"""

    name = "demo"

    def fetch(self) -> List[Competition]:
        today = datetime.now(timezone.utc).date()
        return [
            Competition(
                title="Red Dot Award: Brands & Communication Design 2026",
                competition_type="品牌与传达设计",
                deadline=(today + timedelta(days=45)).isoformat(),
                source_name="红点设计奖",
                source_url="https://www.red-dot.org/",
                description="面向品牌、包装、UI/传达等领域的国际知名设计奖。",
                organizer="Red Dot GmbH",
                region="国际",
                prize="红点至尊奖等",
            ),
            Competition(
                title="A' Design Award & Competition",
                competition_type="综合设计",
                deadline=(today + timedelta(days=28)).isoformat(),
                source_name="A' Design Award",
                source_url="https://competition.adesignaward.com/",
                description="涵盖产品、建筑、平面、时尚等多学科设计竞赛。",
                organizer="OMDESIGN",
                region="国际",
                prize="奖杯、年鉴收录、展览",
            ),
            Competition(
                title="全国大学生广告艺术大赛",
                competition_type="广告 / 视觉传达",
                deadline=(today + timedelta(days=120)).isoformat(),
                source_name="大广赛官网",
                source_url="http://www.sun-ada.net/",
                description="国内高校参与面最广的广告与艺术设计类赛事之一。",
                organizer="大广赛组委会",
                region="中国",
                prize="等级奖、入围奖",
            ),
            Competition(
                title="IF DESIGN STUDENT AWARD",
                competition_type="学生概念设计",
                deadline=(today + timedelta(days=60)).isoformat(),
                source_name="iF Design",
                source_url="https://ifdesign.com/",
                description="面向全球设计院校学生的概念与原型类竞赛。",
                organizer="iF International Forum Design",
                region="国际",
                prize="奖金与全球曝光",
            ),
            Competition(
                title="站酷设计大赛（示例）",
                competition_type="UI / 插画 / 品牌",
                deadline=(today + timedelta(days=14)).isoformat(),
                source_name="站酷",
                source_url="https://www.zcool.com.cn/",
                description="示例条目：可在 config/feeds.json 中配置 RSS 与自建 JSON。",
                organizer="站酷",
                region="中国",
                prize="奖金与商业合作机会",
            ),
        ]
