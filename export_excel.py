from __future__ import annotations

import zipfile
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from models import Competition
from type_simplify import simple_competition_type

EXCEL_PATH = Path(__file__).resolve().parent / "data" / "competitions.xlsx"


def _col_letters(index: int) -> str:
    n = index + 1
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _xml_escape(value: object) -> str:
    return escape(str(value), entities={'"': "&quot;", "'": "&apos;"})


def _build_sheet_xml(rows: list[list[str]]) -> str:
    parts: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
        "<sheetData>",
    ]
    for ri, row in enumerate(rows, start=1):
        parts.append(f'<row r="{ri}">')
        for ci, cell in enumerate(row):
            ref = f"{_col_letters(ci)}{ri}"
            ev = _xml_escape(cell)
            parts.append(f'<c r="{ref}" t="inlineStr"><is><t>{ev}</t></is></c>')
        parts.append("</row>")
    parts.append("</sheetData></worksheet>")
    return "".join(parts)


def competitions_to_excel(items: list[Competition], path: Path | None = None) -> Path:
    target = path or EXCEL_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "比赛名称",
        "类型(简化)",
        "类型(原始)",
        "截止时间",
        "主办方",
        "地区",
        "奖项/奖金",
        "来源站点",
        "详情链接",
        "简介",
        "抓取时间",
    ]
    body: list[list[str]] = [headers]
    for c in items:
        body.append(
            [
                c.title,
                simple_competition_type(c.competition_type),
                c.competition_type,
                c.deadline,
                c.organizer,
                c.region,
                c.prize,
                c.source_name,
                c.source_url,
                c.description,
                c.fetched_at,
            ]
        )
    sheet = _build_sheet_xml(body)
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="设计比赛" sheetId="1" r:id="rId1"/></sheets></workbook>'
    )
    rels_root = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        '</Relationships>'
    )
    rels_wb = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/>'
        '</Relationships>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '</Types>'
    )
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels_root)
        zf.writestr("xl/workbook.xml", workbook)
        zf.writestr("xl/_rels/workbook.xml.rels", rels_wb)
        zf.writestr("xl/worksheets/sheet1.xml", sheet)
    target.write_bytes(buf.getvalue())
    return target
