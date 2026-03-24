#!/usr/bin/env python3
"""生成新闻幻灯片HTML并截图PNG"""
import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

HTML_TEMPLATE_DIR = Path(__file__).parent.parent


def create_slide1_cover(title, subtitle, tag, output_dir):
    """第1页：封面"""
    html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
* {{ margin:0;padding:0;box-sizing:border-box; }}
body {{ width:1080px;height:1440px;background:#0a0a0a;display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;overflow:hidden; }}
.tag {{ background:#e53e3e;color:#fff;font-size:28px;padding:10px 30px;border-radius:6px;letter-spacing:6px;margin-bottom:60px;font-weight:600; }}
h1 {{ font-size:108px;font-weight:900;letter-spacing:12px;margin-bottom:30px; }}
h2 {{ font-size:52px;font-weight:400;color:#e53e3e;letter-spacing:8px;margin-bottom:50px; }}
.divider {{ width:120px;height:3px;background:#555;margin-bottom:50px; }}
.date {{ position:absolute;bottom:60px;font-size:22px;color:#555;letter-spacing:3px; }}
</style></head><body>
<div class="tag">{tag or "新 闻"}</div>
<h1>{title}</h1>
{"<h2>" + subtitle + "</h2>" if subtitle else ""}
<div class="divider"></div>
<div class="date">{datetime.now().strftime("%Y.%m.%d")}</div>
</body></html>'''
    (output_dir / "slide1.html").write_text(html, encoding='utf-8')


def create_slide2_breaking(title, points, output_dir):
    """第2页：突发消息"""
    points_html = "<br>".join(points) if points else "消息内容"
    html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
* {{ margin:0;padding:0;box-sizing:border-box; }}
body {{ width:1080px;height:1440px;background:linear-gradient(180deg,#1a1a2e,#0a0a0a);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;padding:100px 80px;overflow:hidden;position:relative; }}
.hot {{ background:#e53e3e;color:#fff;font-size:24px;padding:8px 24px;border-radius:4px;position:absolute;top:60px;left:80px;font-weight:600; }}
.date {{ font-size:26px;color:#888;margin-bottom:50px;letter-spacing:3px; }}
.text {{ font-size:42px;line-height:2;font-weight:500;letter-spacing:2px;text-align:center; }}
.hl {{ color:#e53e3e;font-weight:700;font-size:48px; }}
</style></head><body>
<div class="hot">🔥 热搜</div>
<div class="date">{datetime.now().strftime("%Y年%m月%d日")}</div>
<div class="text">{points_html}</div>
</body></html>'''
    (output_dir / "slide2.html").write_text(html, encoding='utf-8')


def create_slide3_bio(bio_str, output_dir):
    """第3页：人物介绍"""
    parts = bio_str.split(",") if bio_str else ["未知"]
    name = parts[0] if len(parts) > 0 else ""
    birth = parts[1] if len(parts) > 1 else ""
    origin = parts[2] if len(parts) > 2 else ""
    role = parts[3] if len(parts) > 3 else ""
    highlight = parts[4] if len(parts) > 4 else ""
    
    html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
* {{ margin:0;padding:0;box-sizing:border-box; }}
body {{ width:1080px;height:1440px;background:#0f0f0f;display:flex;flex-direction:column;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;padding:80px;overflow:hidden; }}
.section {{ font-size:24px;color:#e53e3e;letter-spacing:6px;margin-bottom:20px;font-weight:600; }}
h2 {{ font-size:56px;font-weight:800;margin-bottom:60px;letter-spacing:4px; }}
.grid {{ display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-bottom:60px; }}
.card {{ background:rgba(255,255,255,0.05);border-radius:16px;padding:36px;border-left:4px solid #e53e3e; }}
.label {{ font-size:22px;color:#888;margin-bottom:12px; }}
.value {{ font-size:34px;font-weight:700; }}
.desc {{ font-size:32px;line-height:2;color:#ccc; }}
.desc em {{ color:#e53e3e;font-style:normal;font-weight:600; }}
</style></head><body>
<div class="section">他 是 谁</div>
<h2>走近{name}</h2>
<div class="grid">
{"<div class='card'><div class='label'>姓名</div><div class='value'>" + name + "</div></div>" if name else ""}
{"<div class='card'><div class='label'>出生</div><div class='value'>" + birth + "年</div></div>" if birth else ""}
{"<div class='card'><div class='label'>籍贯</div><div class='value'>" + origin + "</div></div>" if origin else ""}
{"<div class='card'><div class='label'>身份</div><div class='value'>" + role + "</div></div>" if role else ""}
</div>
{"<div class='desc'>" + highlight + "</div>" if highlight else ""}
</body></html>'''
    (output_dir / "slide3.html").write_text(html, encoding='utf-8')


def create_slide4_points(points, quote_text, output_dir):
    """第4页：要点盘点"""
    points_html = ""
    for p in (points or []):
        points_html += f'<div class="point"><span class="pin">📌</span><div class="text"><strong>{p}</strong></div></div>\n'
    
    quote_html = ""
    if quote_text:
        quote_html = f'<div class="qbox"><div class="qtext">"{quote_text}"</div></div>'
    
    html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
* {{ margin:0;padding:0;box-sizing:border-box; }}
body {{ width:1080px;height:1440px;background:#0a0a0a;display:flex;flex-direction:column;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;padding:80px;overflow:hidden; }}
.section {{ font-size:24px;color:#e53e3e;letter-spacing:6px;margin-bottom:20px;font-weight:600; }}
h2 {{ font-size:52px;font-weight:800;margin-bottom:50px; }}
.point {{ display:flex;align-items:flex-start;margin-bottom:36px;padding:28px 32px;background:rgba(255,255,255,0.04);border-radius:12px; }}
.pin {{ font-size:28px;margin-right:24px;margin-top:4px; }}
.text {{ font-size:32px;line-height:1.8;color:#ddd; }}
.text strong {{ color:#fff;font-weight:700; }}
.qbox {{ margin-top:40px;padding:36px;border-left:4px solid #e53e3e;background:rgba(229,62,62,0.06);border-radius:0 12px 12px 0; }}
.qtext {{ font-size:30px;line-height:2;color:#e8a0a0; }}
</style></head><body>
<div class="section">要 点 盘 点</div>
<h2>关键信息</h2>
{points_html}
{quote_html}
</body></html>'''
    (output_dir / "slide4.html").write_text(html, encoding='utf-8')


def create_slide5_warning(warning, symptoms, output_dir):
    """第5页：警示信息"""
    sym_html = ""
    for s in (symptoms or []):
        sym_html += f'<div class="sym"><span class="si">🔸</span><span class="st">{s}</span></div>\n'
    
    html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
* {{ margin:0;padding:0;box-sizing:border-box; }}
body {{ width:1080px;height:1440px;background:linear-gradient(180deg,#1a0a0a,#0a0a0a);display:flex;flex-direction:column;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;padding:80px;overflow:hidden; }}
.section {{ font-size:24px;color:#e53e3e;letter-spacing:6px;margin-bottom:20px;font-weight:600; }}
h2 {{ font-size:48px;font-weight:800;margin-bottom:50px;line-height:1.4; }}
.wbox {{ background:rgba(229,62,62,0.1);border:2px solid rgba(229,62,62,0.3);border-radius:16px;padding:48px;text-align:center;margin-bottom:50px; }}
.wbig {{ font-size:80px;font-weight:900;color:#e53e3e;margin-bottom:16px; }}
.wlabel {{ font-size:30px;color:#e8a0a0;letter-spacing:4px; }}
.sym {{ display:flex;align-items:center;margin-bottom:24px;padding:20px 28px;background:rgba(255,255,255,0.04);border-radius:10px; }}
.si {{ font-size:28px;margin-right:20px; }}
.st {{ font-size:30px;color:#ddd;letter-spacing:2px; }}
.footer {{ margin-top:40px;text-align:center;font-size:26px;color:#e53e3e;font-weight:600; }}
</style></head><body>
<div class="section">关 键 信 息</div>
<h2>重要提醒</h2>
{"<div class='wbox'><div class='wbig'>" + warning + "</div></div>" if warning else ""}
{sym_html}
<div class="footer">请务必重视以上信号！</div>
</body></html>'''
    (output_dir / "slide5.html").write_text(html, encoding='utf-8')


def create_slide6_comments(quotes, output_dir):
    """第6页：网友评论"""
    q_html = ""
    for q in (quotes or []):
        parts = q.split(":")
        text = parts[0]
        likes = parts[1] if len(parts) > 1 else ""
        q_html += f'''<div class="cmt"><div class="ct">"{text}"</div>
<div class="cm"><span class="lk">❤️ {likes}</span></div></div>\n'''
    
    html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
* {{ margin:0;padding:0;box-sizing:border-box; }}
body {{ width:1080px;height:1440px;background:#0a0a0a;display:flex;flex-direction:column;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;padding:80px;overflow:hidden; }}
.section {{ font-size:24px;color:#e53e3e;letter-spacing:6px;margin-bottom:20px;font-weight:600; }}
h2 {{ font-size:52px;font-weight:800;margin-bottom:50px; }}
.cmt {{ background:rgba(255,255,255,0.04);border-radius:16px;padding:32px 36px;margin-bottom:24px;border-left:3px solid rgba(229,62,62,0.4); }}
.ct {{ font-size:30px;line-height:1.8;color:#ddd;margin-bottom:12px; }}
.cm {{ display:flex;justify-content:space-between; }}
.lk {{ font-size:22px;color:#e53e3e; }}
</style></head><body>
<div class="section">网 友 留 言</div>
<h2>评论区</h2>
{q_html}
</body></html>'''
    (output_dir / "slide6.html").write_text(html, encoding='utf-8')


def create_slide7_quote(output_dir):
    """第7页：警示金句"""
    html = '''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
* { margin:0;padding:0;box-sizing:border-box; }
body { width:1080px;height:1440px;background:linear-gradient(180deg,#0a0a0a,#1a0a0a,#0a0a0a);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;padding:80px;overflow:hidden;text-align:center; }
.section { font-size:24px;color:#e53e3e;letter-spacing:6px;margin-bottom:30px;font-weight:600; }
.q { font-size:44px;line-height:2.2;color:#ccc;letter-spacing:2px;margin-bottom:50px; }
.q em { color:#e53e3e;font-style:normal;font-weight:700; }
.div { width:80px;height:3px;background:#e53e3e;margin-bottom:50px; }
.msg { font-size:60px;font-weight:900;color:#e53e3e;letter-spacing:8px;margin-bottom:20px; }
</style></head><body>
<div class="section">警 示</div>
<div class="q">你熬的每一个夜<br>身体都记得<br><br>别再说<em>"我还年轻"</em></div>
<div class="div"></div>
<div class="msg">健康不是第一</div>
<div class="msg">是唯一</div>
</body></html>'''
    (output_dir / "slide7.html").write_text(html, encoding='utf-8')


def create_slide8_farewell(title, birth_year, output_dir):
    """第8页：告别页"""
    year = datetime.now().year
    html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
* {{ margin:0;padding:0;box-sizing:border-box; }}
body {{ width:1080px;height:1440px;background:#000;display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#fff;overflow:hidden;text-align:center; }}
.candle {{ font-size:80px;margin-bottom:50px; }}
h1 {{ font-size:72px;font-weight:900;letter-spacing:10px;margin-bottom:30px; }}
.sub {{ font-size:34px;color:#aaa;letter-spacing:4px;margin-bottom:60px;line-height:2; }}
.div {{ width:60px;height:2px;background:#444;margin-bottom:60px; }}
.msg {{ font-size:32px;color:#888;letter-spacing:3px;line-height:2.2; }}
.msg em {{ color:#e53e3e;font-style:normal;font-weight:600; }}
.years {{ margin-top:60px;font-size:36px;color:#555;letter-spacing:6px; }}
</style></head><body>
<div class="candle">🕯️</div>
<h1>一路走好</h1>
<div class="sub">感谢你留下的每一份光</div>
<div class="div"></div>
<div class="msg">珍惜当下，关注<em>健康</em></div>
<div class="years">{title} · {birth_year or "?"}—{year}</div>
</body></html>'''
    (output_dir / "slide8.html").write_text(html, encoding='utf-8')


def html_to_png(html_path, png_path):
    """用Playwright将HTML截图为PNG"""
    script = f'''
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({{"width": 1080, "height": 1440}})
        await page.goto("file://{html_path.resolve()}", wait_until="networkidle")
        await page.screenshot(path="{png_path.resolve()}", type="png",
            clip={{"x": 0, "y": 0, "width": 1080, "height": 1440}})
        await browser.close()

asyncio.run(main())
'''
    subprocess.run(["python3", "-c", script], check=True, capture_output=True)


def main():
    parser = argparse.ArgumentParser(description="生成新闻幻灯片")
    parser.add_argument("--title", required=True, help="新闻标题")
    parser.add_argument("--subtitle", default="", help="副标题")
    parser.add_argument("--tag", default="新闻", help="左上角标签")
    parser.add_argument("--points", nargs="*", default=[], help="要点列表")
    parser.add_argument("--bio", default="", help="人物信息")
    parser.add_argument("--quotes", nargs="*", default=[], help="网友评论")
    parser.add_argument("--warning", default="", help="警示信息")
    parser.add_argument("--symptoms", nargs="*", default=[], help="症状/要点")
    parser.add_argument("--birth-year", default="", help="出生年份")
    parser.add_argument("--quote-text", default="", help="引用语")
    parser.add_argument("--output", default="./slides_output", help="输出目录")
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("📄 生成幻灯片HTML...")
    create_slide1_cover(args.title, args.subtitle, args.tag, output_dir)
    create_slide2_breaking(args.title, args.points, output_dir)
    create_slide3_bio(args.bio, output_dir)
    create_slide4_points(args.points, args.quote_text, output_dir)
    create_slide5_warning(args.warning, args.symptoms, output_dir)
    create_slide6_comments(args.quotes, output_dir)
    create_slide7_quote(output_dir)
    create_slide8_farewell(args.title, args.birth_year or args.bio.split(",")[1] if args.bio and "," in args.bio else "", output_dir)
    
    print("🖼️ 截图生成PNG...")
    for i in range(1, 9):
        html_file = output_dir / f"slide{i}.html"
        png_file = output_dir / f"slide{i}.png"
        html_to_png(html_file, png_file)
        print(f"   ✅ slide{i}.png")
    
    print(f"\n✅ 8张幻灯片已生成到: {output_dir}")


if __name__ == "__main__":
    main()
