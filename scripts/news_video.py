#!/usr/bin/env python3
"""新闻视频生成 — 支持多条新闻合并为一个视频"""
import argparse
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime


def html_slide(html, path):
    """写HTML并截图"""
    path = Path(path)
    path.write_text(html, encoding='utf-8')
    png_path = path.with_suffix('.png')
    script = f'''
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = await b.new_page()
        await page.set_viewport_size({{"width":1080,"height":1440}})
        await page.goto("file://{path.resolve()}", wait_until="networkidle")
        await page.screenshot(path="{png_path.resolve()}", type="png", clip={{"x":0,"y":0,"width":1080,"height":1440}})
        await b.close()
asyncio.run(main())'''
    subprocess.run(["python3","-c",script], capture_output=True)
    return png_path


def gen_cover(title, sub, tag):
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1440px;background:#0a0a0a;display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;overflow:hidden;position:relative}}
.tag{{background:#e53e3e;color:#fff;font-size:28px;padding:10px 30px;border-radius:6px;letter-spacing:6px;margin-bottom:60px;font-weight:600}}
h1{{font-size:86px;font-weight:900;letter-spacing:8px;text-align:center;line-height:1.4;max-width:900px}}
h2{{font-size:36px;font-weight:400;color:#e53e3e;letter-spacing:4px;margin-top:30px;text-align:center;line-height:1.5;padding:0 40px}}
.date{{position:absolute;bottom:60px;font-size:22px;color:#555;letter-spacing:3px}}
</style></head><body>
<div class="tag">{tag}</div>
<h1>{title}</h1>
{"<h2>"+sub+"</h2>" if sub else ""}
<div class="date">{datetime.now().strftime("%Y.%m.%d")}</div></body></html>'''


def gen_news_title(news_num, title, sub):
    """每条新闻的标题页（醒目大字）"""
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1440px;background:#0a0a0a;display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;overflow:hidden;position:relative}}
.num{{font-size:120px;font-weight:900;color:rgba(229,62,62,0.15);position:absolute;top:60px;right:80px;letter-spacing:6px}}
.dot{{width:8px;height:8px;background:#e53e3e;border-radius:50%;margin-bottom:30px}}
h1{{font-size:72px;font-weight:900;letter-spacing:6px;text-align:center;line-height:1.5;max-width:900px;margin-bottom:24px}}
h2{{font-size:32px;font-weight:400;color:#e53e3e;letter-spacing:4px;text-align:center;line-height:1.6;padding:0 60px}}
</style></head><body>
<div class="num">#{news_num:02d}</div>
<div class="dot"></div>
<h1>{title}</h1>
{"<h2>"+sub+"</h2>" if sub else ""}
</body></html>'''


def gen_content(bullets, timeline):
    """要点 + 时间线 + 经济影响合并页"""
    items = ""
    for b in (bullets or []):
        items += f'<div class="item"><span class="dot">▸</span><span class="txt">{b}</span></div>\n'
    
    tl = ""
    for t in (timeline or []):
        tl += f'<div class="ev"><div class="mk"></div><div class="cv">{t}</div></div>\n'
    
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1440px;background:#0f0f0f;display:flex;flex-direction:column;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;padding:60px 80px;overflow:hidden}}
.sec{{font-size:22px;color:#e53e3e;letter-spacing:6px;margin-bottom:12px;font-weight:600}}
h3{{font-size:42px;font-weight:800;margin-bottom:24px;letter-spacing:2px}}
.item{{display:flex;align-items:flex-start;margin-bottom:14px;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.05)}}
.dot{{color:#e53e3e;font-size:28px;margin-right:14px;flex-shrink:0;margin-top:2px}}
.txt{{font-size:28px;line-height:1.7;color:#ddd}}
.divider{{width:100%;height:1px;background:rgba(229,62,62,0.2);margin:20px 0}}
.ev{{display:flex;align-items:flex-start;margin-bottom:10px;position:relative}}
.mk{{width:12px;height:12px;background:#e53e3e;border-radius:50%;flex-shrink:0;margin-top:6px}}
.cv{{margin-left:16px;font-size:24px;line-height:1.7;color:#ccc;padding:8px 16px;background:rgba(255,255,255,0.03);border-radius:8px;flex:1}}
</style></head><body>
<div class="sec">新 闻 要 点</div>
<h3>核心信息</h3>
{items}
<div class="divider"></div>
<div class="sec">事 件 脉 络</div>
<h3>时间线</h3>
{tl}
</body></html>'''


def gen_impact(title, impact_lines):
    """经济影响/展望页"""
    lines = ""
    for l in (impact_lines or []):
        lines += f'<div class="line">{l}</div>\n'
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1440px;background:#0a0a0a;display:flex;flex-direction:column;justify-content:center;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;padding:80px;overflow:hidden}}
.sec{{font-size:22px;color:#e53e3e;letter-spacing:6px;margin-bottom:20px;font-weight:600}}
h3{{font-size:48px;font-weight:800;margin-bottom:40px;letter-spacing:3px}}
.line{{font-size:30px;line-height:2;color:#ccc;margin-bottom:16px;padding-left:20px;border-left:3px solid rgba(229,62,62,0.4)}}
.line em{{color:#e53e3e;font-style:normal;font-weight:600}}
</style></head><body>
<div class="sec">影 响 分 析</div>
<h3>{title}</h3>
{lines}
</body></html>'''


def make_video(pngs, output, bgm_path=None, per_page=4.0, fade=0.8):
    """将多张PNG合成一个视频"""
    n = len(pngs)
    page_dur = per_page
    total = n * page_dur
    
    inputs = " ".join(f'-loop 1 -t {page_dur+(0.8 if i==n-1 else 0):.1f} -i "{p}"' for i, p in enumerate(pngs))
    
    filters = []
    for i in range(n):
        filters.append(f'[{i}:v]scale=1080:1440,format=yuv420p,setsar=1[v{i}]')
    
    offset = page_dur
    prev = "v0"
    for i in range(1, n):
        curr = f'm{i}'
        filters.append(f'[{prev}][v{i}]xfade=transition=fade:duration={fade}:offset={offset:.1f}[{curr}]')
        prev = curr
        offset += page_dur
    
    vstream = prev if prev.startswith('m') else 'v0'
    
    noaudio = "/tmp/_video_noaudio.mp4"
    cmd = f'ffmpeg -y {inputs} -filter_complex "{";".join(filters)}" -map "[{vstream}]" -c:v libx264 -pix_fmt yuv420p -r 30 "{noaudio}"'
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"   ⚠️ 视频合成失败: {r.stderr[-200:]}")
        return False
    
    if bgm_path and Path(bgm_path).exists():
        final_dur = total + 0.8
        bgm_trimmed = "/tmp/_bgm_trimmed.mp3"
        subprocess.run(f'ffmpeg -y -ss 5 -i "{bgm_path}" -t {final_dur:.0f} -af "afade=t=in:st=0:d=1.5,afade=t=out:st={final_dur-2:.0f}:d=2,volume=0.5" -ar 44100 -ac 2 "{bgm_trimmed}"', shell=True, capture_output=True)
        subprocess.run(f'ffmpeg -y -i "{noaudio}" -i "{bgm_trimmed}" -c:v copy -c:a aac -b:a 128k -shortest "{output}"', shell=True, capture_output=True)
    else:
        Path(noaudio).rename(output)
    
    return Path(output).exists()


def main():
    parser = argparse.ArgumentParser(description="新闻视频生成（多条合并）")
    parser.add_argument("--config", help="JSON配置文件路径")
    parser.add_argument("--title", default="", help="合并视频标题")
    parser.add_argument("--tags", default="", help="合并标签（逗号分隔）")
    parser.add_argument("--bgm", default="", help="BGM关键词或文件路径")
    parser.add_argument("--output", default="./news_output", help="输出目录")
    parser.add_argument("--publish", action="store_true", help="发布到抖音")
    parser.add_argument("--douyin-title", default="", help="抖音标题（不填用title）")
    parser.add_argument("--douyin-tags", default="", help="抖音话题（不填用tags）")
    args = parser.parse_args()
    
    if not args.config:
        print("❌ 需要 --config 参数（JSON配置文件）")
        sys.exit(1)
    
    config = json.loads(Path(args.config).read_text())
    news_list = config.get("news", [])
    title = config.get("title", args.title)
    tags = config.get("tags", args.tags)
    bgm = config.get("bgm", args.bgm)
    
    if not news_list:
        print("❌ 配置中没有新闻")
        sys.exit(1)
    
    output_dir = Path(config.get("output", args.output))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成封面
    tag = tags.split(",")[0] if tags else "新闻速递"
    print(f"📄 生成封面...")
    cover_html = gen_cover(title, f"共 {len(news_list)} 条重要新闻", tag)
    pngs = [html_slide(cover_html, str(output_dir / "slide_00_cover.html"))]
    print(f"   ✅ 封面")
    
    # 为每条新闻生成3页
    for i, news in enumerate(news_list, 1):
        print(f"📄 [{i}/{len(news_list)}] {news.get('title','')[:20]}...")
        
        # 1) 标题页（醒目大字）
        title_html = gen_news_title(i, news.get("title",""), news.get("subtitle",""))
        p = html_slide(title_html, str(output_dir / f"slide_{i}a_title.html"))
        pngs.append(p)
        print(f"   ✅ 标题页")
        
        # 2) 要点+时间线
        content_html = gen_content(news.get("bullets",[]), news.get("timeline",[]))
        p = html_slide(content_html, str(output_dir / f"slide_{i}b_content.html"))
        pngs.append(p)
        print(f"   ✅ 要点+时间线")
        
        # 3) 影响分析
        impact_title = news.get("impact_title", "经济影响")
        impact_html = gen_impact(impact_title, news.get("impact",[]))
        p = html_slide(impact_html, str(output_dir / f"slide_{i}c_impact.html"))
        pngs.append(p)
        print(f"   ✅ 影响分析")
    
    # 合成视频
    video_path = output_dir / "final.mp4"
    print(f"\n🎬 合成视频 ({len(pngs)} 页, ~{len(pngs)*4:.0f}秒)...")
    
    # 处理BGM
    bgm_path = None
    if bgm:
        if Path(bgm).exists():
            bgm_path = bgm
        else:
            print(f"🎵 搜索BGM: {bgm}")
            r = subprocess.run(["yt-dlp","-x","--audio-format","mp3","--no-check-certificates",
                               "-o","/tmp/_news_bgm.%(ext)s", f"ytsearch1:{bgm}"],
                              capture_output=True, text=True)
            if Path("/tmp/_news_bgm.mp3").exists():
                bgm_path = "/tmp/_news_bgm.mp3"
                print(f"   ✅ BGM已下载")
            else:
                print(f"   ⚠️ BGM下载失败，无音乐版本")
    
    ok = make_video(pngs, str(video_path), bgm_path, per_page=4.0, fade=0.8)
    
    if ok:
        size = video_path.stat().st_size / 1024 / 1024
        print(f"✅ 视频已生成: {video_path} ({size:.1f}MB)")
        
        # 发布抖音
        publish = config.get("publish", args.publish)
        if publish:
            dy_title = config.get("douyin_title", args.douyin_title or title)
            dy_tags = config.get("douyin_tags", args.douyin_tags or tags)
            print(f"\n📱 发布抖音...")
            script = Path(__file__).parent / "douyin_publish.py"
            cmd = f'python3 "{script}" --video "{video_path}" --title "{dy_title}" --tags "{dy_tags}"'
            r = subprocess.run(cmd, shell=True, capture_output=False)
            if r.returncode == 0:
                print("✅ 抖音发布成功！")
            else:
                print("❌ 抖音发布失败")
    else:
        print("❌ 视频生成失败")
    
    # 清理
    for f in Path("/tmp").glob("_news_*"):
        f.unlink(missing_ok=True)
    for f in Path("/tmp").glob("_video_*"):
        f.unlink(missing_ok=True)
    for f in Path("/tmp").glob("_bgm_*"):
        f.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
