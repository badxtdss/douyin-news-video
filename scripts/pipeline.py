#!/usr/bin/env python3
"""一键全流程：生成幻灯片 → 合成视频 → 配乐 → 发布抖音"""
import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent


def run_script(cmd, desc):
    """执行脚本并输出"""
    print(f"\n{'='*50}")
    print(f"📌 {desc}")
    print(f"{'='*50}\n")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ {desc} 失败")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="抖音新闻视频一键全流程")
    
    # 内容参数
    parser.add_argument("--title", required=True, help="新闻标题")
    parser.add_argument("--subtitle", default="", help="副标题")
    parser.add_argument("--tag", default="新闻", help="标签")
    parser.add_argument("--points", nargs="*", default=[], help="要点")
    parser.add_argument("--bio", default="", help="人物信息")
    parser.add_argument("--quotes", nargs="*", default=[], help="网友评论")
    parser.add_argument("--warning", default="", help="警示信息")
    parser.add_argument("--symptoms", nargs="*", default=[], help="症状列表")
    parser.add_argument("--birth-year", default="", help="出生年份")
    parser.add_argument("--quote-text", default="", help="引用语")
    
    # 视频参数
    parser.add_argument("--bgm", default="起风了 纯音乐", help="BGM关键词")
    parser.add_argument("--duration", type=int, default=28, help="视频时长")
    
    # 抖音参数
    parser.add_argument("--publish", action="store_true", help="是否发布到抖音")
    parser.add_argument("--douyin-title", default="", help="抖音标题")
    parser.add_argument("--douyin-tags", default="", help="抖音话题")
    parser.add_argument("--schedule", default=None, help="定时发布")
    
    # 输出
    parser.add_argument("--output", default="./douyin_news_output", help="输出目录")
    
    args = parser.parse_args()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    video_path = output_dir / "final.mp4"
    
    # 第1步：生成幻灯片
    slides_cmd = f'''python3 "{SCRIPTS_DIR}/create_slides.py" \
        --title "{args.title}" \
        --subtitle "{args.subtitle}" \
        --tag "{args.tag}" \
        --points {" ".join(f'"{p}"' for p in args.points)} \
        --bio "{args.bio}" \
        --quotes {" ".join(f'"{q}"' for q in args.quotes)} \
        --warning "{args.warning}" \
        --symptoms {" ".join(f'"{s}"' for s in args.symptoms)} \
        --birth-year "{args.birth_year}" \
        --quote-text "{args.quote_text}" \
        --output "{output_dir}"'''
    run_script(slides_cmd, "第1步：生成幻灯片")
    
    # 第2步：合成视频+配乐
    video_cmd = f'''python3 "{SCRIPTS_DIR}/make_video.py" \
        --slides "{output_dir}" \
        --bgm "{args.bgm}" \
        --duration {args.duration} \
        --output "{video_path}"'''
    run_script(video_cmd, "第2步：合成视频+配乐")
    
    # 第3步：发布到抖音
    if args.publish:
        douyin_title = args.douyin_title or args.title
        schedule_arg = f'--schedule "{args.schedule}"' if args.schedule else ""
        publish_cmd = f'''python3 "{SCRIPTS_DIR}/douyin_publish.py" \
            --video "{video_path}" \
            --title "{douyin_title}" \
            --tags "{args.douyin_tags}" \
            {schedule_arg}'''
        run_script(publish_cmd, "第3步：发布到抖音")
    
    print(f"\n{'='*50}")
    print("🎉 全流程完成！")
    print(f"{'='*50}")
    print(f"📁 输出目录: {output_dir}")
    print(f"📹 视频文件: {video_path}")
    print(f"🖼️ 幻灯片: {output_dir}/slide[1-8].png")


if __name__ == "__main__":
    main()
