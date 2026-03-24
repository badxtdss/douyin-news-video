#!/usr/bin/env python3
"""生成新闻幻灯片 — 智能分析内容，自适应排版"""
import argparse
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime


def auto_detect_type(title, content):
    """根据标题和内容自动判断新闻类型"""
    text = (title + " " + content).lower()
    
    death_words = ["去世", "逝世", "离世", "走了", "病逝", "享年", "享寿", "一路走好", "悼念", "追悼"]
    finance_words = ["美元", "亿", "股价", "暴跌", "暴涨", "交易", "市场", "投资", "空单", "期货", "盈利", "亏损", "内幕"]
    politics_words = ["总统", "国会", "参议员", "白宫", "选举", "弹劾", "制裁", "外交", "会谈"]
    tech_words = ["ai", "人工智能", "芯片", "发布", "上市", "融资", "科技"]
    sports_words = ["比赛", "冠军", "世界杯", "奥运", "进球", "决赛", "联赛"]
    
    scores = {
        "death": sum(1 for w in death_words if w in text),
        "finance": sum(1 for w in finance_words if w in text),
        "politics": sum(1 for w in politics_words if w in text),
        "tech": sum(1 for w in tech_words if w in text),
        "sports": sum(1 for w in sports_words if w in text),
    }
    
    # 如果有去世相关词且得分最高，归为death
    if scores["death"] >= 2:
        return "death"
    
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "general"


def html_slide(filename, html):
    """写入HTML文件"""
    return html


def gen_slide1_cover(title, subtitle, tag):
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1440px;background:#0a0a0a;display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;overflow:hidden}}
.tag{{background:#e53e3e;color:#fff;font-size:28px;padding:10px 30px;border-radius:6px;letter-spacing:6px;margin-bottom:60px;font-weight:600}}
h1{{font-size:100px;font-weight:900;letter-spacing:10px;margin-bottom:30px;text-align:center;line-height:1.3}}
h2{{font-size:36px;font-weight:400;color:#e53e3e;letter-spacing:4px;margin-bottom:50px;text-align:center;line-height:1.5;padding:0 40px}}
.date{{position:absolute;bottom:60px;font-size:22px;color:#555;letter-spacing:3px}}
</style></head><body>
<div class="tag">{tag or "新 闻"}</div>
<h1>{title}</h1>
{"<h2>" + subtitle + "</h2>" if subtitle else ""}
<div class="date">{datetime.now().strftime("%Y.%m.%d")}</div>
</body></html>'''


def gen_slide2_summary(headline, bullets):
    """第2页：摘要/要点"""
    items = ""
    for b in (bullets or []):
        items += f'<div class="item"><span class="dot">▸</span><span class="txt">{b}</span></div>\n'
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1440px;background:linear-gradient(180deg,#1a1a2e,#0a0a0a);display:flex;flex-direction:column;justify-content:center;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;padding:100px 80px;overflow:hidden}}
.hot{{background:#e53e3e;color:#fff;font-size:24px;padding:8px 24px;border-radius:4px;position:absolute;top:60px;left:80px;font-weight:600}}
.headline{{font-size:40px;font-weight:700;margin-bottom:50px;line-height:1.6;letter-spacing:2px}}
.item{{display:flex;align-items:flex-start;margin-bottom:30px;padding:20px 0;border-bottom:1px solid rgba(255,255,255,0.06)}}
.dot{{color:#e53e3e;font-size:32px;margin-right:20px;flex-shrink:0;margin-top:2px}}
.txt{{font-size:32px;line-height:1.8;color:#ddd}}
</style></head><body>
<div class="hot">🔥 热点</div>
<div class="headline">{headline}</div>
{items}
</body></html>'''


def gen_slide3_context(title, context_lines):
    """第3页：背景/上下文"""
    lines_html = ""
    for line in (context_lines or []):
        lines_html += f'<div class="line">{line}</div>\n'
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1440px;background:#0f0f0f;display:flex;flex-direction:column;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;padding:80px;overflow:hidden}}
.section{{font-size:24px;color:#e53e3e;letter-spacing:6px;margin-bottom:20px;font-weight:600}}
h2{{font-size:52px;font-weight:800;margin-bottom:50px;letter-spacing:4px}}
.line{{font-size:32px;line-height:2;color:#ccc;margin-bottom:20px;padding-left:20px;border-left:3px solid rgba(229,62,62,0.4)}}
.line em{{color:#e53e3e;font-style:normal;font-weight:600}}
</style></head><body>
<div class="section">背 景</div>
<h2>{title}</h2>
{lines_html}
</body></html>'''


def gen_slide4_data(key_data):
    """第4页：关键数据/数字"""
    cards_html = ""
    for item in (key_data or []):
        if ":" in item:
            label, value = item.split(":", 1)
            cards_html += f'''<div class="card">
<div class="val">{value.strip()}</div>
<div class="lab">{label.strip()}</div>
</div>\n'''
        else:
            cards_html += f'<div class="card"><div class="val full">{item}</div></div>\n'
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1440px;background:#0a0a0a;display:flex;flex-direction:column;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;padding:80px;overflow:hidden}}
.section{{font-size:24px;color:#e53e3e;letter-spacing:6px;margin-bottom:30px;font-weight:600}}
h2{{font-size:52px;font-weight:800;margin-bottom:50px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:30px}}
.card{{background:rgba(229,62,62,0.08);border:1px solid rgba(229,62,62,0.2);border-radius:16px;padding:40px 30px;text-align:center}}
.val{{font-size:48px;font-weight:900;color:#e53e3e;margin-bottom:10px}}
.val.full{{font-size:36px;color:#fff}}
.lab{{font-size:24px;color:#999;letter-spacing:2px}}
</style></head><body>
<div class="section">关 键 数 据</div>
<h2>核心信息</h2>
<div class="grid">{cards_html}</div>
</body></html>'''


def gen_slide5_timeline(events):
    """第5页：时间线/事件"""
    items = ""
    for i, ev in enumerate(events or []):
        items += f'''<div class="event">
<div class="marker"></div>
<div class="line_v"></div>
<div class="content">{ev}</div>
</div>\n'''
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1440px;background:#0a0a0a;display:flex;flex-direction:column;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;padding:80px;overflow:hidden}}
.section{{font-size:24px;color:#e53e3e;letter-spacing:6px;margin-bottom:20px;font-weight:600}}
h2{{font-size:52px;font-weight:800;margin-bottom:50px}}
.event{{display:flex;align-items:flex-start;margin-bottom:30px;position:relative}}
.marker{{width:16px;height:16px;background:#e53e3e;border-radius:50%;flex-shrink:0;margin-top:8px;z-index:1}}
.line_v{{position:absolute;left:7px;top:24px;bottom:-30px;width:2px;background:rgba(229,62,62,0.3)}}
.event:last-child .line_v{{display:none}}
.content{{margin-left:24px;font-size:30px;line-height:1.8;color:#ddd;padding:12px 24px;background:rgba(255,255,255,0.04);border-radius:10px;flex:1}}
</style></head><body>
<div class="section">事 件 梳 理</div>
<h2>时间线</h2>
{items}
</body></html>'''


def gen_slide6_quotes(quotes):
    """第6页：各方反应/引用"""
    q_html = ""
    for q in (quotes or []):
        parts = q.split(":")
        text = parts[0].strip()
        source = parts[1].strip() if len(parts) > 1 else ""
        q_html += f'''<div class="quote">
<div class="qt">"{text}"</div>
{"<div class='qs'>—— " + source + "</div>" if source else ""}
</div>\n'''
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1440px;background:#0a0a0a;display:flex;flex-direction:column;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;padding:80px;overflow:hidden}}
.section{{font-size:24px;color:#e53e3e;letter-spacing:6px;margin-bottom:20px;font-weight:600}}
h2{{font-size:52px;font-weight:800;margin-bottom:40px}}
.quote{{background:rgba(255,255,255,0.04);border-radius:16px;padding:30px 36px;margin-bottom:24px;border-left:3px solid rgba(229,62,62,0.4)}}
.qt{{font-size:30px;line-height:1.8;color:#ddd;margin-bottom:10px}}
.qs{{font-size:22px;color:#e53e3e;text-align:right}}
</style></head><body>
<div class="section">各 方 反 应</div>
<h2>声音</h2>
{q_html}
</body></html>'''


def gen_slide7_highlight(highlight_text):
    """第7页：核心观点/金句"""
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1440px;background:linear-gradient(180deg,#0a0a0a,#1a0a0a,#0a0a0a);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;padding:100px;overflow:hidden;text-align:center}}
.section{{font-size:24px;color:#e53e3e;letter-spacing:6px;margin-bottom:50px;font-weight:600}}
.quote{{font-size:44px;line-height:2;color:#ccc;letter-spacing:2px}}
.quote em{{color:#e53e3e;font-style:normal;font-weight:700}}
</style></head><body>
<div class="section">核 心 观 点</div>
<div class="quote">{highlight_text}</div>
</body></html>'''


def gen_slide8_ending(title, ending_text):
    """第8页：结尾/关注提示"""
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1440px;background:#000;display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;overflow:hidden;text-align:center}}
.icon{{font-size:60px;margin-bottom:40px}}
h1{{font-size:64px;font-weight:900;letter-spacing:8px;margin-bottom:30px}}
.sub{{font-size:32px;color:#aaa;letter-spacing:4px;line-height:2;margin-bottom:50px}}
.div{{width:60px;height:2px;background:#444;margin-bottom:50px}}
.msg{{font-size:28px;color:#666;letter-spacing:3px}}
</style></head><body>
<div class="icon">📰</div>
<h1>{title}</h1>
<div class="sub">{ending_text or "持续关注，了解更多真相"}</div>
<div class="div"></div>
<div class="msg">关注我，不错过每一条重要新闻</div>
</body></html>'''


def html_to_png(html_content, png_path):
    """将HTML内容写文件并截图为PNG"""
    html_path = Path("/tmp") / f"slide_{Path(png_path).stem}.html"
    html_path.write_text(html_content, encoding='utf-8')
    
    script = f'''
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({{"width": 1080, "height": 1440}})
        await page.goto("file://{html_path.resolve()}", wait_until="networkidle")
        await page.screenshot(path="{Path(png_path).resolve()}", type="png",
            clip={{"x": 0, "y": 0, "width": 1080, "height": 1440}})
        await browser.close()

asyncio.run(main())
'''
    result = subprocess.run(["python3", "-c", script], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   ⚠️ 截图失败: {result.stderr[:100]}")


def main():
    parser = argparse.ArgumentParser(description="智能新闻幻灯片生成")
    parser.add_argument("--title", required=True, help="新闻标题")
    parser.add_argument("--subtitle", default="", help="副标题")
    parser.add_argument("--tag", default="", help="左上角标签（不填则自动判断）")
    
    # 内容（灵活输入）
    parser.add_argument("--bullets", nargs="*", default=[], help="要点列表")
    parser.add_argument("--context", nargs="*", default=[], help="背景信息")
    parser.add_argument("--data", nargs="*", default=[], help="关键数据（格式：标签:数值）")
    parser.add_argument("--timeline", nargs="*", default=[], help="时间线事件")
    parser.add_argument("--quotes", nargs="*", default=[], help="各方引用（格式：内容:来源）")
    parser.add_argument("--highlight", default="", help="核心观点/金句")
    parser.add_argument("--ending", default="", help="结尾文字")
    
    # 兼容旧格式
    parser.add_argument("--points", nargs="*", default=[], help="要点（兼容旧版）")
    parser.add_argument("--bio", default="", help="人物信息（兼容旧版）")
    parser.add_argument("--warning", default="", help="警示（兼容旧版）")
    parser.add_argument("--symptoms", nargs="*", default=[], help="症状/要点（兼容旧版）")
    
    parser.add_argument("--output", default="./slides_output", help="输出目录")
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 合并新旧参数
    bullets = args.bullets or args.points
    context = args.context or args.symptoms
    data = args.data
    if args.warning:
        data = data or [args.warning]
    if args.bio:
        context = context or [args.bio]
    
    # 自动判断标签
    tag = args.tag
    if not tag:
        news_type = auto_detect_type(args.title, " ".join(bullets + context))
        type_tags = {
            "death": "沉痛悼念", "finance": "国际财经", "politics": "时政要闻",
            "tech": "科技前沿", "sports": "体育赛事", "general": "新闻速递"
        }
        tag = type_tags.get(news_type, "新闻速递")
    
    # 自动生成高亮（如果没提供）
    highlight = args.highlight
    if not highlight and bullets:
        highlight = bullets[0]
    
    # 自动生成结尾（如果没提供）
    ending = args.ending
    if not ending:
        ending = "持续关注，了解更多真相"
    
    print(f"📄 生成幻灯片 (标签: {tag})...")
    
    slides = [
        ("slide1", gen_slide1_cover(args.title, args.subtitle, tag)),
        ("slide2", gen_slide2_summary(args.title, bullets)),
        ("slide3", gen_slide3_context("背景梳理", context)),
        ("slide4", gen_slide4_data(data)),
        ("slide5", gen_slide5_timeline(timeline if (timeline := args.timeline) else bullets)),
        ("slide6", gen_slide6_quotes(args.quotes)),
        ("slide7", gen_slide7_highlight(highlight)),
        ("slide8", gen_slide8_ending(args.title, ending)),
    ]
    
    print("🖼️ 截图生成PNG...")
    for name, html in slides:
        png_path = output_dir / f"{name}.png"
        html_to_png(html, png_path)
        print(f"   ✅ {name}.png")
    
    print(f"\n✅ 8张幻灯片已生成到: {output_dir}")


if __name__ == "__main__":
    main()
