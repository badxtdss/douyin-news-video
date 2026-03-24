#!/usr/bin/env python3
"""新闻视频生成 — 配TTS配音，多条新闻合并"""
import argparse
import subprocess
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

EDGE_TTS_SCRIPT = '''
import asyncio
import edge_tts

async def run():
    text = open("{txt}", encoding="utf-8").read()
    communicate = edge_tts.Communicate(text, "{voice}")
    await communicate.save("{out}")

asyncio.run(run())
'''

DEFAULT_VOICE = "zh-CN-YunxiNeural"


def ensure_edge_tts():
    try:
        import edge_tts
    except ImportError:
        subprocess.run(["pip", "install", "edge-tts"], capture_output=True)
        import edge_tts


def gen_tts(text, output_path, voice=DEFAULT_VOICE):
    """生成TTS音频"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 先将文字写入临时文件（避免转义问题）
    txt_path = output_path.with_suffix('.txt')
    txt_path.write_text(text, encoding='utf-8')
    
    script = EDGE_TTS_SCRIPT.format(txt=str(txt_path.resolve()), voice=voice, out=str(output_path.resolve()))
    r = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=30)
    
    txt_path.unlink(missing_ok=True)
    return output_path.exists()


def get_audio_duration(path):
    """获取音频时长"""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except:
        return 4.0


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


# ========== HTML 模板 ==========

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
    items = ""
    for b in (bullets or []):
        items += f'<div class="item"><span class="dot2">▸</span><span class="txt">{b}</span></div>\n'
    tl = ""
    for t in (timeline or []):
        tl += f'<div class="ev"><div class="mk"></div><div class="cv">{t}</div></div>\n'
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1440px;background:#0f0f0f;display:flex;flex-direction:column;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;padding:60px 80px;overflow:hidden}}
.sec{{font-size:22px;color:#e53e3e;letter-spacing:6px;margin-bottom:12px;font-weight:600}}
h3{{font-size:42px;font-weight:800;margin-bottom:24px;letter-spacing:2px}}
.item{{display:flex;align-items:flex-start;margin-bottom:14px;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.05)}}
.dot2{{color:#e53e3e;font-size:28px;margin-right:14px;flex-shrink:0;margin-top:2px}}
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
    lines = ""
    for l in (impact_lines or []):
        # 去掉HTML标签用于TTS
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


# ========== TTS 文案 ==========

def tts_text_for_cover(title, sub):
    text = title
    if sub:
        text += "。" + sub.replace("\n", "，")
    return text


def tts_text_for_news_title(news_num, title, sub):
    text = f"第{news_num}条。{title}"
    if sub:
        text += "。" + sub
    return text


def tts_text_for_content(bullets, timeline):
    parts = []
    if bullets:
        parts.append("新闻要点。")
        for b in bullets:
            parts.append(b + "。")
    if timeline:
        parts.append("时间线。")
        for t in timeline:
            parts.append(t + "。")
    return " ".join(parts)


def tts_text_for_impact(title, impact_lines):
    parts = [f"{title}。"]
    for l in impact_lines:
        # 去掉HTML标签
        import re
        clean = re.sub(r'<[^>]+>', '', l)
        parts.append(clean + "。")
    return " ".join(parts)


# ========== 核心逻辑 ==========

def make_video_with_audio(pngs, audios, output, bgm_path=None):
    """图片+音频合成视频，每张图的停留=对应音频时长"""
    n = len(pngs)
    inputs = []
    filter_parts = []
    
    # 为每个slide生成带音频的视频片段
    segments = []
    for i in range(n):
        png = str(pngs[i])
        audio = str(audios[i]) if audios[i] else None
        seg = f"/tmp/_seg_{i}.mp4"
        
        if audio and Path(audio).exists():
            # 图片 + 音频
            cmd = f'ffmpeg -y -loop 1 -i "{png}" -i "{audio}" -c:v libx264 -c:a aac -b:a 128k -pix_fmt yuv420p -r 30 -shortest -vf "scale=1080:1440,setsar=1" "{seg}"'
        else:
            # 无音频，4秒静音
            cmd = f'ffmpeg -y -loop 1 -t 4 -i "{png}" -f lavfi -t 4 -i anullsrc=r=44100:cl=stereo -c:v libx264 -c:a aac -pix_fmt yuv420p -r 30 -vf "scale=1080:1440,setsar=1" "{seg}"'
        
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"   ⚠️ 片段{i}合成失败")
            continue
        segments.append(seg)
    
    if not segments:
        return False
    
    # 拼接所有片段（带fade转场）
    concat_list = "/tmp/_concat.txt"
    with open(concat_list, "w") as f:
        for seg in segments:
            f.write(f"file '{seg}'\n")
    
    noaudio = "/tmp/_merged.mp4"
    subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{concat_list}" -c copy "{noaudio}"',
                   shell=True, capture_output=True)
    
    # 加BGM
    if bgm_path and Path(bgm_path).exists():
        # 获取总时长
        dur_r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                                "-of","default=noprint_wrappers=1:nokey=1",noaudio],
                               capture_output=True, text=True)
        try:
            total_dur = float(dur_r.stdout.strip())
        except:
            total_dur = 30
        
        bgm_trimmed = "/tmp/_bgm_trimmed.mp3"
        subprocess.run(f'ffmpeg -y -ss 5 -i "{bgm_path}" -t {total_dur:.0f} '
                       f'-af "afade=t=in:st=0:d=1.5,afade=t=out:st={max(total_dur-2,0):.0f}:d=2,volume=0.25" '
                       f'-ar 44100 -ac 2 "{bgm_trimmed}"',
                       shell=True, capture_output=True)
        
        # 旁白+BGM混合
        subprocess.run(f'ffmpeg -y -i "{noaudio}" -i "{bgm_trimmed}" '
                       f'-filter_complex "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[aout]" '
                       f'-map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k "{output}"',
                       shell=True, capture_output=True)
    else:
        Path(noaudio).rename(output)
    
    return Path(output).exists()


def main():
    parser = argparse.ArgumentParser(description="新闻视频生成（TTS配音）")
    parser.add_argument("--config", help="JSON配置文件路径")
    parser.add_argument("--title", default="")
    parser.add_argument("--tags", default="")
    parser.add_argument("--bgm", default="")
    parser.add_argument("--output", default="./news_output")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="TTS语音（zh-CN-YunxiNeural 男声 / zh-CN-XiaoxiaoNeural 女声）")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--douyin-title", default="")
    parser.add_argument("--douyin-tags", default="")
    args = parser.parse_args()
    
    if not args.config:
        print("❌ 需要 --config 参数")
        sys.exit(1)
    
    ensure_edge_tts()
    
    config = json.loads(Path(args.config).read_text())
    news_list = config.get("news", [])
    title = config.get("title", args.title)
    tags = config.get("tags", args.tags)
    bgm = config.get("bgm", args.bgm)
    voice = config.get("voice", args.voice)
    
    if not news_list:
        print("❌ 没有新闻"); sys.exit(1)
    
    output_dir = Path(config.get("output", args.output))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    pngs = []
    audios = []
    tts_dir = output_dir / "tts"
    tts_dir.mkdir(exist_ok=True)
    
    # 封面
    tag = tags.split(",")[0] if tags else "新闻速递"
    print("📄 生成封面...")
    cover_html = gen_cover(title, f"共 {len(news_list)} 条重要新闻", tag)
    p = html_slide(cover_html, str(output_dir / "slide_00_cover.html"))
    pngs.append(p)
    
    # 封面TTS
    cover_tts = tts_text_for_cover(title, f"共{len(news_list)}条重要新闻")
    a = tts_dir / "audio_00_cover.mp3"
    gen_tts(cover_tts, str(a), voice)
    audios.append(a)
    print(f"   ✅ 封面（含配音）")
    
    # 每条新闻3页
    for i, news in enumerate(news_list, 1):
        news_title = news.get("title","")
        print(f"📄 [{i}/{len(news_list)}] {news_title[:20]}...")
        
        # 1) 标题页
        t_html = gen_news_title(i, news_title, news.get("subtitle",""))
        p = html_slide(t_html, str(output_dir / f"slide_{i}a_title.html"))
        pngs.append(p)
        t_text = tts_text_for_news_title(i, news_title, news.get("subtitle",""))
        a = tts_dir / f"audio_{i}a_title.mp3"
        gen_tts(t_text, str(a), voice)
        audios.append(a)
        print(f"   ✅ 标题页（含配音）")
        
        # 2) 要点+时间线
        c_html = gen_content(news.get("bullets",[]), news.get("timeline",[]))
        p = html_slide(c_html, str(output_dir / f"slide_{i}b_content.html"))
        pngs.append(p)
        c_text = tts_text_for_content(news.get("bullets",[]), news.get("timeline",[]))
        a = tts_dir / f"audio_{i}b_content.mp3"
        gen_tts(c_text, str(a), voice)
        audios.append(a)
        print(f"   ✅ 要点+时间线（含配音）")
        
        # 3) 影响分析
        imp_title = news.get("impact_title", "经济影响")
        imp_html = gen_impact(imp_title, news.get("impact",[]))
        p = html_slide(imp_html, str(output_dir / f"slide_{i}c_impact.html"))
        pngs.append(p)
        imp_text = tts_text_for_impact(imp_title, news.get("impact",[]))
        a = tts_dir / f"audio_{i}c_impact.mp3"
        gen_tts(imp_text, str(a), voice)
        audios.append(a)
        print(f"   ✅ 影响分析（含配音）")
    
    # 合成视频
    video_path = output_dir / "final.mp4"
    print(f"\n🎬 合成视频（TTS配音 + 图片）...")
    
    bgm_path = None
    if bgm:
        if Path(bgm).exists():
            bgm_path = bgm
        else:
            print(f"🎵 搜索BGM: {bgm}")
            subprocess.run(["yt-dlp","-x","--audio-format","mp3","--no-check-certificates",
                           "-o","/tmp/_news_bgm.%(ext)s", f"ytsearch1:{bgm}"],
                          capture_output=True)
            if Path("/tmp/_news_bgm.mp3").exists():
                bgm_path = "/tmp/_news_bgm.mp3"
                print(f"   ✅ BGM已下载")
    
    ok = make_video_with_audio(pngs, audios, str(video_path), bgm_path)
    
    if ok:
        size = video_path.stat().st_size / 1024 / 1024
        print(f"✅ 视频已生成: {video_path} ({size:.1f}MB)")
        
        publish = config.get("publish", args.publish)
        if publish:
            dy_title = config.get("douyin_title", args.douyin_title or title)
            dy_tags = config.get("douyin_tags", args.douyin_tags or tags)
            print(f"\n📱 发布抖音...")
            script = Path(__file__).parent / "douyin_publish.py"
            subprocess.run(f'python3 "{script}" --video "{video_path}" --title "{dy_title}" --tags "{dy_tags}"',
                          shell=True)
    
    # 清理临时文件
    Path("/tmp/_concat.txt").unlink(missing_ok=True)
    for f in Path("/tmp").glob("_seg_*"):
        f.unlink(missing_ok=True)
    for f in Path("/tmp").glob("_news_*"):
        f.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
