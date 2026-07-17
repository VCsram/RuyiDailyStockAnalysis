"""
通过 AdsPower Local API 打开指纹浏览器，爬取「贵州茅台」近期新闻。

前置：
1. AdsPower 已启动，Local API 正常（默认 http://127.0.0.1:50325）
2. 本目录放置凭证（已 gitignore），或设置环境变量：
   - adspower_api_key.txt  / ADSPOWER_API_KEY
   - adspower_profile_id.txt / ADSPOWER_PROFILE_ID（环境编号 / user_id）
3. 依赖：pip install playwright && playwright install chromium

用法：
  python 07_AdsPower爬取茅台新闻.py
  python 07_AdsPower爬取茅台新闻.py --list-only   # 仅列出环境，不爬取
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
API_BASE = os.environ.get("ADSPOWER_API_BASE", "http://127.0.0.1:50325").rstrip("/")
QUERY = "贵州茅台"
SEARCH_URL = "https://www.baidu.com/s?" + urllib.parse.urlencode(
    {"wd": f"{QUERY} 新闻", "rn": "20"}
)


def _read_secret(filename: str, env_name: str) -> str:
    env_val = (os.environ.get(env_name) or "").strip()
    if env_val:
        return env_val
    path = HERE / filename
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return ""


def _api_get(path: str, api_key: str, params: dict | None = None) -> dict:
    qs = urllib.parse.urlencode(params or {})
    url = f"{API_BASE}{path}"
    if qs:
        url = f"{url}?{qs}"
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} {url}: {body}") from e


def check_status() -> None:
    data = _api_get("/status", api_key="")
    if data.get("code") != 0:
        raise RuntimeError(f"AdsPower status 异常: {data}")


def list_profiles(api_key: str, page_size: int = 20) -> list[dict]:
    data = _api_get(
        "/api/v1/user/list",
        api_key,
        {"page": "1", "page_size": str(page_size)},
    )
    if data.get("code") != 0:
        raise RuntimeError(f"列出环境失败: {data}")
    return (data.get("data") or {}).get("list") or []


def start_browser(api_key: str, user_id: str) -> dict:
    data = _api_get(
        "/api/v1/browser/start",
        api_key,
        {"user_id": user_id},
    )
    if data.get("code") != 0:
        raise RuntimeError(f"启动浏览器失败: {data}")
    return data["data"]


def stop_browser(api_key: str, user_id: str) -> None:
    try:
        _api_get("/api/v1/browser/stop", api_key, {"user_id": user_id})
    except Exception as exc:  # noqa: BLE001 — 收尾尽量不阻断
        print(f"[warn] 关闭浏览器失败: {exc}", file=sys.stderr)


def scrape_baidu_news(cdp_http: str) -> list[dict]:
    from playwright.sync_api import sync_playwright

    items: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_http)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_timeout(2500)

        # 百度搜索结果：标题链接
        cards = page.query_selector_all("#content_left .result, #content_left .c-container")
        for card in cards[:20]:
            a = card.query_selector("h3 a") or card.query_selector("a")
            if not a:
                continue
            title = (a.inner_text() or "").strip().replace("\n", " ")
            href = a.get_attribute("href") or ""
            if not title or QUERY not in title and QUERY not in (card.inner_text() or ""):
                # 放宽：只要结果卡片文本含茅台/关键词相关也保留
                text = (card.inner_text() or "")
                if "茅台" not in text and "600519" not in text:
                    continue
            # 尝试取摘要与时间
            abstract_el = card.query_selector(".c-abstract, .content-right_8Zs40, span")
            abstract = (abstract_el.inner_text() if abstract_el else "")[:300]
            time_el = card.query_selector(".c-color-gray2, .c-color-text, .news-source_XernM")
            pub_time = (time_el.inner_text() if time_el else "").strip()[:80]
            items.append(
                {
                    "title": title,
                    "url": href,
                    "snippet": abstract.strip(),
                    "time_hint": pub_time,
                    "source": "baidu_search",
                }
            )

        # 若百度结构变化导致为空，再试东方财富资讯搜索
        if not items:
            em_url = (
                "https://so.eastmoney.com/news/s?"
                + urllib.parse.urlencode({"keyword": QUERY})
            )
            page.goto(em_url, wait_until="domcontentloaded", timeout=60_000)
            page.wait_for_timeout(3000)
            links = page.query_selector_all("a")
            seen = set()
            for a in links:
                title = (a.inner_text() or "").strip().replace("\n", " ")
                href = a.get_attribute("href") or ""
                if len(title) < 8 or "茅台" not in title:
                    continue
                if href in seen:
                    continue
                if not href.startswith("http"):
                    continue
                seen.add(href)
                items.append(
                    {
                        "title": title[:200],
                        "url": href,
                        "snippet": "",
                        "time_hint": "",
                        "source": "eastmoney_search",
                    }
                )
                if len(items) >= 15:
                    break

        # 不断开 AdsPower 控制的浏览器进程，仅断开 CDP 客户端
        browser.close()
    return items


def save_results(items: list[dict]) -> tuple[Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = HERE / f"adspower_茅台新闻_{stamp}.csv"
    json_path = HERE / f"adspower_茅台新闻_{stamp}.json"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["title", "url", "snippet", "time_hint", "source"]
        )
        w.writeheader()
        w.writerows(items)
    json_path.write_text(
        json.dumps(
            {"query": QUERY, "fetched_at": stamp, "count": len(items), "items": items},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return csv_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="AdsPower 爬取贵州茅台新闻")
    parser.add_argument("--list-only", action="store_true", help="仅列出环境")
    parser.add_argument("--keep-open", action="store_true", help="爬完不关闭浏览器")
    args = parser.parse_args()

    print(f"[1] 检查 AdsPower Local API: {API_BASE}")
    check_status()
    print("    status=ok")

    api_key = _read_secret("adspower_api_key.txt", "ADSPOWER_API_KEY")
    profile_id = _read_secret("adspower_profile_id.txt", "ADSPOWER_PROFILE_ID")

    if not api_key:
        print(
            "\n缺少 API Key。请任选其一：\n"
            "  A) AdsPower → 账号管理/设置 → Local API → 关闭「安全校验」后重试\n"
            "  B) 生成 API Key，写入本目录 adspower_api_key.txt\n"
            "     或设置环境变量 ADSPOWER_API_KEY\n"
            "  另需环境编号写入 adspower_profile_id.txt / ADSPOWER_PROFILE_ID\n",
            file=sys.stderr,
        )
        return 2

    time.sleep(1.1)
    print("[2] 列出指纹环境…")
    try:
        profiles = list_profiles(api_key)
    except Exception as exc:  # noqa: BLE001
        print(f"列出失败: {exc}", file=sys.stderr)
        return 3

    if not profiles:
        print("没有任何指纹环境，请先在 AdsPower 创建环境。", file=sys.stderr)
        return 4

    for p in profiles:
        print(
            f"    - user_id={p.get('user_id')}  name={p.get('name')}  "
            f"serial={p.get('serial_number')}"
        )

    if args.list_only:
        return 0

    if not profile_id:
        profile_id = str(profiles[0].get("user_id") or "")
        print(f"[3] 未指定 profile，使用第一个: {profile_id}")
    else:
        print(f"[3] 使用指定 profile: {profile_id}")

    time.sleep(1.1)
    print("[4] 启动 AdsPower 浏览器…")
    data = start_browser(api_key, profile_id)
    ws = (data.get("ws") or {})
    puppeteer = ws.get("puppeteer") or ""
    debugger = (data.get("webdriver") or "")  # 有时是 selenium 地址
    # CDP HTTP 入口通常是 debuggerAddress，如 127.0.0.1:xxxxx
    debug_addr = data.get("ws", {}).get("selenium") or debugger
    # AdsPower 常见字段：data.ws.puppeteer / data.debug_port / data.webdriver
    cdp_http = ""
    if debug_addr and "://" not in str(debug_addr):
        cdp_http = f"http://{debug_addr}"
    elif isinstance(debug_addr, str) and debug_addr.startswith("http"):
        cdp_http = debug_addr
    else:
        # 从 puppeteer ws 反推 http://host:port
        # ws://127.0.0.1:PORT/devtools/browser/...
        if puppeteer.startswith("ws://"):
            hostport = puppeteer[5:].split("/")[0]
            cdp_http = f"http://{hostport}"

    print(f"    puppeteer={puppeteer[:80]}...")
    print(f"    cdp_http={cdp_http}")
    if not cdp_http:
        print(f"无法解析 CDP 地址，原始 data keys={list(data.keys())}", file=sys.stderr)
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000], file=sys.stderr)
        if not args.keep_open:
            stop_browser(api_key, profile_id)
        return 5

    items: list[dict] = []
    try:
        print(f"[5] 打开搜索页并提取: {QUERY}")
        items = scrape_baidu_news(cdp_http)
        print(f"    抓到 {len(items)} 条")
        for i, it in enumerate(items[:8], 1):
            print(f"    {i}. {it['title'][:60]}")
        csv_path, json_path = save_results(items)
        print(f"[6] 已保存:\n    {csv_path}\n    {json_path}")
    finally:
        if not args.keep_open:
            time.sleep(1.1)
            print("[7] 关闭 AdsPower 浏览器")
            stop_browser(api_key, profile_id)

    return 0 if items else 6


if __name__ == "__main__":
    raise SystemExit(main())
