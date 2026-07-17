# 如意金股 Visual Identity (`dsa_vi`)

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
