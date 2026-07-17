# -*- coding: utf-8 -*-
from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path("docs/练习记录/练习2_Logo与Icon/screenshots")
out.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    page.goto("http://127.0.0.1:8000/", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)
    # open nav drawer for brand mark + wordmark
    btn = page.get_by_role("button", name="打开导航菜单")
    if btn.count():
        btn.first.click()
        page.wait_for_timeout(800)
    page.screenshot(path=str(out / "01_home_sidebar.png"), full_page=False)

    # theme toggle if available
    theme = page.get_by_role("button", name="切换主题")
    if theme.count():
        theme.first.click()
        page.wait_for_timeout(800)
        page.screenshot(path=str(out / "02_home_sidebar_light.png"), full_page=False)

    page.goto(
        "http://127.0.0.1:8000/brand/login-preview.html",
        wait_until="domcontentloaded",
        timeout=30000,
    )
    page.wait_for_timeout(1000)
    page.screenshot(path=str(out / "03_login_preview.png"), full_page=False)

    # favicon presence
    page.goto("http://127.0.0.1:8000/favicon.svg", wait_until="domcontentloaded", timeout=15000)
    page.screenshot(path=str(out / "04_favicon_svg.png"), full_page=False)

    browser.close()

print("shots", sorted(p.name for p in out.glob("*.png")))
