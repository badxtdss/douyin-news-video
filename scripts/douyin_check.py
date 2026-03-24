#!/usr/bin/env python3
"""检查抖音Cookie有效性"""
import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

COOKIE_FILE = Path(__file__).parent.parent / "cookies" / "douyin.json"

async def main():
    print("=" * 50)
    print("抖音 Cookie 有效性检查")
    print("=" * 50)
    
    if not COOKIE_FILE.exists():
        print(f"❌ Cookie 文件不存在: {COOKIE_FILE}")
        print("请运行 douyin_login.py 获取Cookie")
        sys.exit(1)
    
    print(f"Cookie 文件: {COOKIE_FILE}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=str(COOKIE_FILE))
        page = await context.new_page()
        
        await page.goto("https://creator.douyin.com/creator-micro/content/upload", timeout=120000)
        await asyncio.sleep(5)
        
        # 检测是否有登录表单（真正的登录页面）
        login_input = await page.locator('input[placeholder="请输入手机号"]').count()
        body_text = await page.locator('body').inner_text()
        has_creator_login = '创作者登录' in body_text
        
        if login_input > 0 and has_creator_login:
            print("❌ Cookie 已失效，需要重新登录")
            await browser.close()
            sys.exit(1)
        else:
            print("✅ Cookie 有效，已登录状态")
            await browser.close()
            sys.exit(0)

asyncio.run(main())
