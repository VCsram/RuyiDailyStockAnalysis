# -*- coding: utf-8 -*-
from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path("docs/练习记录/练习1_品牌化改造/screenshots")
out.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://127.0.0.1:8000/", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)
    # open mobile/nav if present
    btn = page.get_by_role("button", name="打开导航菜单")
    if btn.count():
        btn.first.click()
        page.wait_for_timeout(800)
    page.screenshot(path=str(out / "01_home_sidebar_pw.png"), full_page=False)

    page.goto("http://127.0.0.1:8000/login", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)
    page.screenshot(path=str(out / "02_login_pw.png"), full_page=False)
    print("title", page.title())
    content = page.content()
    print("brand_zh", "如意金股" in content)
    print("brand_en", "RuyiDailyStockAnalysis" in content)
    print("author", "creeper" in content)
    browser.close()

print("files", sorted(p.name for p in out.glob("*.png")))
