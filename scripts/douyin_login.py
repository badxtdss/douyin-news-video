#!/usr/bin/env python3
"""抖音获取Cookie"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

COOKIE_DIR = Path(__file__).parent.parent / "cookies"
COOKIE_FILE = COOKIE_DIR / "douyin.json"
SCREENSHOT = COOKIE_DIR / "qr_screenshot.png"

async def main():
    COOKIE_DIR.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("正在打开抖音创作者中心...")
        await page.goto("https://creator.douyin.com/", timeout=120000, wait_until="networkidle")
        await asyncio.sleep(3)
        
        await page.screenshot(path=str(SCREENSHOT))
        print(f"📸 页面截图已保存: {SCREENSHOT}")
        print(f"当前 URL: {page.url}")
        
        if 'login' not in page.url.lower() and 'creator' in page.url.lower():
            print("✅ 检测到已登录状态")
        else:
            print("⚠️ 请在浏览器中扫码登录")
            print("登录成功后，请在下方输入 'y' 并回车继续...")
            loop = asyncio.get_event_loop()
            user_input = await loop.run_in_executor(None, input, "已登录? (y/n): ")
            if user_input.strip().lower() != 'y':
                print("取消保存")
                await browser.close()
                return
        
        await asyncio.sleep(2)
        await context.storage_state(path=str(COOKIE_FILE))
        print(f"✅ Cookie 已保存到: {COOKIE_FILE}")
        await browser.close()

asyncio.run(main())
