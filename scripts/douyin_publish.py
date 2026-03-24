#!/usr/bin/env python3
"""抖音视频自动发布"""
import argparse
import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

COOKIE_FILE = Path(__file__).parent.parent / "cookies" / "douyin.json"


async def publish(video_path, title, tags, schedule=None, headless=False):
    """执行发布"""
    video_path = Path(video_path)
    if not video_path.exists():
        print(f"❌ 视频文件不存在: {video_path}")
        return False
    
    if not COOKIE_FILE.exists():
        print("❌ Cookie不存在，请先运行 douyin_login.py")
        return False
    
    title = title[:30]
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    
    print("=" * 50)
    print("抖音视频发布")
    print("=" * 50)
    print(f"视频: {video_path}")
    print(f"标题: {title}")
    print(f"话题: {', '.join(tag_list) if tag_list else '无'}")
    print(f"定时: {schedule or '立即发布'}")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(storage_state=str(COOKIE_FILE))
        page = await context.new_page()
        
        # [1] 打开上传页
        print("[1/6] 打开抖音创作者中心...")
        await page.goto("https://creator.douyin.com/creator-micro/content/upload", timeout=120000)
        await asyncio.sleep(3)
        
        # 登录检测（更精确）
        login_input = await page.locator('input[placeholder="请输入手机号"]').count()
        body_text = await page.locator('body').inner_text()
        if login_input > 0 and '创作者登录' in body_text:
            print("❌ Cookie已失效，请运行 douyin_login.py 重新登录")
            await browser.close()
            return False
        print("   ✅ 已登录")
        
        # [2] 上传视频
        print("[2/6] 上传视频...")
        file_input = page.locator("div[class^='container'] input[type='file']")
        await file_input.set_input_files(str(video_path))
        
        # [3] 等待处理
        print("[3/6] 等待视频处理...")
        for i in range(60):
            if 'publish' in page.url or 'post/video' in page.url:
                break
            await asyncio.sleep(1)
        
        await asyncio.sleep(5)
        for i in range(120):
            if await page.locator('div:has-text("重新上传")').count() > 0:
                print("   ✅ 上传完成")
                break
            if i % 10 == 0 and i > 0:
                print(f"   上传中... ({i}s)")
            await asyncio.sleep(1)
        await asyncio.sleep(2)
        
        # [4] 填写标题
        print("[4/6] 填写标题...")
        try:
            title_area = page.locator(".notranslate")
            await title_area.click()
            await page.keyboard.press("Control+KeyA")
            await page.keyboard.press("Delete")
            await page.keyboard.type(title)
            print("   ✅ 标题OK")
        except Exception as e:
            print(f"   ⚠️ 标题异常: {e}")
        
        # [5] 添加话题
        print("[5/6] 添加话题...")
        try:
            zone = page.locator(".zone-container")
            for tag in tag_list:
                await zone.click()
                await page.keyboard.type("#" + tag)
                await asyncio.sleep(0.3)
                await page.keyboard.press("Space")
                await asyncio.sleep(0.3)
            print(f"   ✅ 已添加 {len(tag_list)} 个话题")
        except Exception as e:
            print(f"   ⚠️ 话题异常: {e}")
        
        # [6] 定时发布
        if schedule:
            print(f"[6/6] 设置定时发布: {schedule}...")
            try:
                label = page.locator("[class^='radio']:has-text('定时发布')")
                await label.click()
                await asyncio.sleep(1)
                await page.locator('.semi-input[placeholder="日期和时间"]').click()
                await page.keyboard.press("Control+KeyA")
                await page.keyboard.type(schedule)
                await page.keyboard.press("Enter")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"   ⚠️ 定时设置异常: {e}")
        else:
            print("[6/6] 立即发布...")
        
        await asyncio.sleep(1)
        
        # 点击发布
        publish_btn = page.get_by_role('button', name='发布', exact=True)
        if await publish_btn.count() > 0:
            await publish_btn.click()
            print("   已点击发布")
            await asyncio.sleep(8)
            
            if 'manage' in page.url:
                print()
                print("=" * 50)
                print("✅ 视频发布成功！")
                print("=" * 50)
            else:
                print(f"   当前URL: {page.url}")
                print("   请检查作品管理确认状态")
        else:
            print("   ❌ 未找到发布按钮")
            await browser.close()
            return False
        
        await context.storage_state(path=str(COOKIE_FILE))
        await asyncio.sleep(2)
        await browser.close()
        return True


def main():
    parser = argparse.ArgumentParser(description="抖音视频发布")
    parser.add_argument("-v", "--video", required=True, help="视频文件路径")
    parser.add_argument("-t", "--title", required=True, help="标题（最多30字）")
    parser.add_argument("-g", "--tags", default="", help="话题标签（逗号分隔）")
    parser.add_argument("-s", "--schedule", default=None, help="定时发布（YYYY-MM-DD HH:MM）")
    parser.add_argument("--headless", action="store_true", help="无头模式")
    args = parser.parse_args()
    
    success = asyncio.run(publish(args.video, args.title, args.tags, args.schedule, args.headless))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
