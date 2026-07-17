# -*- coding: utf-8 -*-
"""Generate RuyiDailyStockAnalysis VI assets under docs/assets/dsa_vi/.

Design selected: 「玉如意弧 · 上升折线 · AI 节点」
- Ruyi-inspired S-curve (如意)
- Ascending market polyline (金融走势)
- Node accents (AI 量化)
Readable at 16px.
"""
from __future__ import annotations

import shutil
import struct
import zlib
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
WEB_BRAND = ROOT.parents[2] / "apps" / "dsa-web" / "public" / "brand"
WEB_PUBLIC = ROOT.parents[2] / "apps" / "dsa-web" / "public"
PNG_SIZES = (16, 32, 48, 64, 128, 180, 256, 512)
ICO_SIZES = (16, 32, 48, 64, 128, 256)

# Palette
EMERALD = "#10B981"
EMERALD_DEEP = "#059669"
SKY = "#38BDF8"
INK = "#0F172A"
INK_SOFT = "#334155"
PAPER = "#F8FAFC"
WHITE = "#FFFFFF"


def icon_mark_svg(*, bg: str | None, stroke_main: str, stroke_accent: str, fill_node: str) -> str:
    """512 viewBox mark: ruyi arc + rising polyline + nodes."""
    bg_layer = (
        f'<rect x="32" y="32" width="448" height="448" rx="112" fill="{bg}"/>'
        if bg
        else ""
    )
    # Ruyi-like arc (left) + rising chart (right)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="如意金股">
  <title>如意金股 Icon</title>
  {bg_layer}
  <!-- Ruyi arc -->
  <path d="M148 360 C148 250 210 210 268 210 C310 210 334 236 334 274 C334 320 286 334 248 318"
        fill="none" stroke="{stroke_main}" stroke-width="36" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M248 318 C210 300 188 318 188 352 C188 392 230 412 278 392"
        fill="none" stroke="{stroke_main}" stroke-width="36" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- Rising quant line -->
  <path d="M196 348 L252 292 L300 318 L372 210"
        fill="none" stroke="{stroke_accent}" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- AI nodes -->
  <circle cx="196" cy="348" r="18" fill="{fill_node}"/>
  <circle cx="252" cy="292" r="18" fill="{fill_node}"/>
  <circle cx="300" cy="318" r="18" fill="{fill_node}"/>
  <circle cx="372" cy="210" r="22" fill="{stroke_accent}"/>
</svg>
"""


def wordmark_svg(*, theme: str) -> str:
    """Horizontal logo: mark + ZH + EN."""
    if theme == "light":
        text_primary = INK
        text_secondary = INK_SOFT
        mark_bg = EMERALD_DEEP
        mark_main = WHITE
        mark_accent = SKY
        node = WHITE
    else:
        text_primary = PAPER
        text_secondary = "#94A3B8"
        mark_bg = EMERALD
        mark_main = WHITE
        mark_accent = "#A7F3D0"
        node = WHITE

    # Inline compact mark at x=0
    mark = f"""
  <g transform="translate(0,16)">
    <rect x="0" y="0" width="128" height="128" rx="32" fill="{mark_bg}"/>
    <path d="M37 90 C37 62 52 52 67 52 C78 52 84 58 84 68 C84 80 72 83 62 79"
          fill="none" stroke="{mark_main}" stroke-width="9" stroke-linecap="round"/>
    <path d="M62 79 C52 74 47 79 47 87 C47 97 58 102 70 97"
          fill="none" stroke="{mark_main}" stroke-width="9" stroke-linecap="round"/>
    <path d="M49 87 L63 73 L75 80 L93 53"
          fill="none" stroke="{mark_accent}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="49" cy="87" r="4.5" fill="{node}"/>
    <circle cx="63" cy="73" r="4.5" fill="{node}"/>
    <circle cx="75" cy="80" r="4.5" fill="{node}"/>
    <circle cx="93" cy="53" r="5.5" fill="{mark_accent}"/>
  </g>
"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 160" role="img" aria-label="如意金股 RuyiDailyStockAnalysis">
  <title>如意金股 Logo ({theme})</title>
  {mark}
  <text x="160" y="78" font-family="Segoe UI, PingFang SC, Microsoft YaHei, sans-serif"
        font-size="52" font-weight="700" fill="{text_primary}">如意金股</text>
  <text x="160" y="122" font-family="Segoe UI, Helvetica Neue, Arial, sans-serif"
        font-size="22" font-weight="560" letter-spacing="1.2" fill="{text_secondary}">RuyiDailyStockAnalysis</text>
</svg>
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"wrote {path.relative_to(ROOT.parent.parent.parent) if False else path}")


def assert_svg_parseable(path: Path) -> None:
    ET.parse(path)


def render_icon_png(size: int, out: Path, *, with_bg: bool) -> None:
    """Rasterize mark with PIL (deterministic, no extra deps)."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    s = size / 512.0

    def sx(v: float) -> float:
        return v * s

    if with_bg:
        pad = sx(32)
        draw.rounded_rectangle(
            [pad, pad, size - pad, size - pad],
            radius=sx(112),
            fill=(5, 150, 105, 255),  # EMERALD_DEEP
        )
        main = (255, 255, 255, 255)
        accent = (56, 189, 248, 255)
        node = (255, 255, 255, 255)
    else:
        main = (16, 185, 129, 255)
        accent = (56, 189, 248, 255)
        node = (14, 165, 233, 255)

    # Approximate arcs with thick polylines for small-size clarity
    w = max(2, int(round(36 * s)))
    # Ruyi body
    ruyi = [
        (sx(148), sx(360)),
        (sx(160), sx(280)),
        (sx(210), sx(220)),
        (sx(268), sx(210)),
        (sx(320), sx(230)),
        (sx(334), sx(274)),
        (sx(300), sx(320)),
        (sx(248), sx(318)),
        (sx(200), sx(330)),
        (sx(188), sx(352)),
        (sx(220), sx(400)),
        (sx(278), sx(392)),
    ]
    draw.line(ruyi, fill=main, width=w, joint="curve")
    chart = [
        (sx(196), sx(348)),
        (sx(252), sx(292)),
        (sx(300), sx(318)),
        (sx(372), sx(210)),
    ]
    draw.line(chart, fill=accent, width=max(2, int(round(28 * s))), joint="curve")
    for i, (x, y) in enumerate(chart):
        r = sx(18 if i < 3 else 22)
        fill = node if i < 3 else accent
        draw.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    img.save(out, format="PNG")


def png_chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def ico_from_pngs(png_paths: list[Path], out: Path) -> None:
    """Build multi-size ICO embedding PNG images (Vista+)."""
    entries = []
    images = []
    for p in png_paths:
        data = p.read_bytes()
        img = Image.open(p)
        w, h = img.size
        entries.append((w if w < 256 else 0, h if h < 256 else 0, data))
        images.append(data)

    # ICONDIR
    count = len(entries)
    offset = 6 + 16 * count
    buf = bytearray()
    buf += struct.pack("<HHH", 0, 1, count)
    data_blobs = []
    for w, h, data in entries:
        data_blobs.append(data)
        buf += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    for data in data_blobs:
        buf += data
    out.write_bytes(bytes(buf))
    print(f"wrote ICO {out} ({count} sizes)")


def write_readme() -> None:
    text = """# 如意金股 Visual Identity (`dsa_vi`)

## 品牌
- 中文名：如意金股
- 英文名：RuyiDailyStockAnalysis
- 作者：creeper

## 设计方向（评估后选定）

1. **如意结缠绕 K 线** — 文化符号强，但 16px 结线易糊。
2. **几何「如」字标 + AI 节点** — 辨识偏汉字本体，跨语言弱。
3. **玉如意弧 + 上升折线 + AI 节点（选定）** — 同时表达「如意 / 金融走势 / AI 量化」；粗线 + 节点在 16px 仍可辨。

## 文件

| 文件 | 说明 |
|------|------|
| `icon.svg` | 透明底主标（应用内 favicon / 侧栏 mark） |
| `logo-light.svg` | 浅色背景横版 Logo（深色字） |
| `logo-dark.svg` | 深色背景横版 Logo（浅色字） |
| `favicon.ico` | 多尺寸 ICO（16/32/48/64/128/256） |
| `png/icon-{size}.png` | 带圆角底色的应用图标导出 |

Web 运行时副本：`apps/dsa-web/public/brand/`，根目录另有 `favicon.svg` / `favicon.ico`。

## 再生

```bash
python docs/assets/dsa_vi/build_brand_assets.py
```
"""
    write_text(ROOT / "README.md", text)


def sync_to_web() -> None:
    WEB_BRAND.mkdir(parents=True, exist_ok=True)
    for name in ("icon.svg", "logo-light.svg", "logo-dark.svg", "favicon.ico"):
        src = ROOT / name
        shutil.copy2(src, WEB_BRAND / name)
    # Also expose root favicons expected by index.html
    shutil.copy2(ROOT / "icon.svg", WEB_PUBLIC / "favicon.svg")
    shutil.copy2(ROOT / "favicon.ico", WEB_PUBLIC / "favicon.ico")
    # Keep brand folder copies of favicon.svg alias
    shutil.copy2(ROOT / "icon.svg", WEB_BRAND / "favicon.svg")
    # Copy pngs
    png_dir = WEB_BRAND / "png"
    png_dir.mkdir(exist_ok=True)
    for p in (ROOT / "png").glob("*.png"):
        shutil.copy2(p, png_dir / p.name)
    print(f"synced -> {WEB_BRAND}")


def verify() -> None:
    for name in ("icon.svg", "logo-light.svg", "logo-dark.svg"):
        assert_svg_parseable(ROOT / name)
        print(f"SVG OK {name}")
    for size in PNG_SIZES:
        p = ROOT / "png" / f"icon-{size}.png"
        img = Image.open(p)
        assert img.size == (size, size), (p, img.size)
        print(f"PNG OK {p.name} {img.size}")
    ico = Image.open(ROOT / "favicon.ico")
    # Pillow may only expose one size; check file has multiple ICONDIRENTRY
    raw = (ROOT / "favicon.ico").read_bytes()
    _reserved, itype, count = struct.unpack_from("<HHH", raw, 0)
    assert itype == 1 and count >= 4, (itype, count)
    print(f"ICO OK entries={count}")


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / "png").mkdir(exist_ok=True)

    write_text(
        ROOT / "icon.svg",
        icon_mark_svg(bg=None, stroke_main=EMERALD, stroke_accent=SKY, fill_node=EMERALD_DEEP),
    )
    write_text(ROOT / "logo-light.svg", wordmark_svg(theme="light"))
    write_text(ROOT / "logo-dark.svg", wordmark_svg(theme="dark"))
    # favicon.svg content = icon with solid bg for tab clarity
    write_text(
        ROOT / "favicon.svg",
        icon_mark_svg(bg=EMERALD_DEEP, stroke_main=WHITE, stroke_accent=SKY, fill_node=WHITE),
    )

    pngs_for_ico: list[Path] = []
    for size in PNG_SIZES:
        out = ROOT / "png" / f"icon-{size}.png"
        render_icon_png(size, out, with_bg=True)
        if size in ICO_SIZES:
            pngs_for_ico.append(out)

    ico_from_pngs(pngs_for_ico, ROOT / "favicon.ico")
    # Also store a copy named as requested
    shutil.copy2(ROOT / "favicon.ico", ROOT / "icon.ico")

    write_readme()
    sync_to_web()
    verify()
    print("DONE")


if __name__ == "__main__":
    main()
