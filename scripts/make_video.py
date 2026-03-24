#!/usr/bin/env python3
"""将幻灯片PNG合成为视频并添加BGM"""
import argparse
import subprocess
import sys
import json
from pathlib import Path


def run(cmd):
    """执行命令"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 命令失败: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout


def find_bgm(keyword):
    """通过YouTube搜索并下载BGM"""
    print(f"🎵 搜索BGM: {keyword}")
    
    # 搜索
    cmd = f'yt-dlp --flat-playlist -j "ytsearch3:{keyword} 纯音乐" 2>/dev/null'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    best = None
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        try:
            d = json.loads(line)
            duration = d.get("duration", 999)
            title = d.get("title", "")
            # 优先选择3-8分钟的纯音乐
            if 120 < duration < 600:
                best = d
                break
            if not best and duration > 60:
                best = d
        except:
            continue
    
    if not best:
        print("⚠️ 未找到合适BGM，使用无音乐模式")
        return None
    
    video_id = best["id"]
    title = best.get("title", "unknown")
    print(f"   选中: {title}")
    
    # 下载
    bgm_path = Path("/tmp") / f"bgm_{video_id}.mp3"
    run(f'yt-dlp -x --audio-format mp3 --audio-quality 0 -o "{bgm_path}" "https://www.youtube.com/watch?v={video_id}" 2>/dev/null')
    
    if bgm_path.exists():
        print(f"   ✅ BGM已下载: {bgm_path}")
        return bgm_path
    else:
        print("   ⚠️ BGM下载失败")
        return None


def make_video(slides_dir, bgm_path, duration, output_path):
    """合成视频"""
    slides_dir = Path(slides_dir)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 检查幻灯片
    slides = sorted(slides_dir.glob("slide*.png"))
    if len(slides) < 2:
        print(f"❌ 幻灯片不足，找到 {len(slides)} 张")
        sys.exit(1)
    
    n = len(slides)
    page_duration = duration / n
    fade_duration = 0.8
    
    print(f"🎬 合成视频: {n}张幻灯片, 每页{page_duration:.1f}秒")
    
    # 构建ffmpeg滤镜
    inputs = []
    scales = []
    for i in range(n):
        inputs.append(f"-loop 1 -t {page_duration + fade_duration} -i {slides[i]}")
        scales.append(f"[{i}:v]scale=1080:1440,format=yuv420p,setsar=1[v{i}]")
    
    # xfade链
    xfade_chain = "[v0][v1]xfade=transition=fade:duration=0.8:offset={offset}[m01]"
    offsets = [page_duration]
    for i in range(2, n):
        prev = f"m{i-2}{i-1}" if i > 2 else "m01"
        curr = f"m{i-1}{i}"
        offset = offsets[-1] + page_duration
        offsets.append(offset)
        xfade_chain += f";\n[{prev}][v{i}]xfade=transition=fade:duration=0.8:offset={offset:.2f}[{curr}]"
    
    final = f"m{n-2}{n-1}"
    
    filter_complex = ";\n".join(scales) + ";\n" + xfade_chain
    
    total_with_fade = duration + (n - 1) * fade_duration
    
    cmd = f'ffmpeg -y {" ".join(inputs)} -filter_complex "{filter_complex}" -map "[{final}]" -c:v libx264 -pix_fmt yuv420p -r 30 -t {total_with_fade:.2f} /tmp/video_no_audio.mp4 2>&1'
    
    run(cmd)
    print("   ✅ 视频合成完成")
    
    # 添加BGM
    if bgm_path and Path(bgm_path).exists():
        print("🎵 添加BGM...")
        # 裁剪BGM到指定时长，加淡入淡出
        bgm_trimmed = "/tmp/bgm_trimmed.mp3"
        fade_out_start = duration - 2
        run(f'ffmpeg -y -ss 25 -i "{bgm_path}" -t {duration} -af "afade=t=in:st=0:d=1.5,afade=t=out:st={fade_out_start}:d=2,volume=0.5" -ar 44100 -ac 2 {bgm_trimmed} 2>&1')
        
        # 合成
        run(f'ffmpeg -y -i /tmp/video_no_audio.mp4 -i {bgm_trimmed} -c:v copy -c:a aac -b:a 128k -shortest "{output_path}" 2>&1')
        print(f"   ✅ 视频+音乐合成完成")
    else:
        # 无音乐，静音音轨
        run(f'ffmpeg -y -i /tmp/video_no_audio.mp4 -f lavfi -i anullsrc -c:v copy -c:a aac -shortest "{output_path}" 2>&1')
        print("   ✅ 视频合成完成（无音乐）")
    
    # 清理临时文件
    for f in ["/tmp/video_no_audio.mp4", "/tmp/bgm_trimmed.mp3"]:
        Path(f).unlink(missing_ok=True)
    
    # 输出信息
    info = run(f'ffprobe -i "{output_path}" -show_entries format=duration,size -show_entries stream=codec_name,width,height -v quiet -of json')
    print(f"\n📦 输出文件: {output_path}")
    print(f"   大小: {output_path.stat().st_size / 1024:.0f}KB")


def main():
    parser = argparse.ArgumentParser(description="幻灯片合成视频+配乐")
    parser.add_argument("--slides", required=True, help="幻灯片目录")
    parser.add_argument("--bgm", default="", help="BGM关键词（自动搜索）或音乐文件路径")
    parser.add_argument("--duration", type=int, default=28, help="视频时长（秒）")
    parser.add_argument("--output", default="./output_video.mp4", help="输出文件路径")
    args = parser.parse_args()
    
    # 获取BGM
    bgm_path = None
    if args.bgm:
        if Path(args.bgm).exists():
            bgm_path = args.bgm
        else:
            bgm_path = find_bgm(args.bgm)
    
    # 合成视频
    make_video(args.slides, bgm_path, args.duration, args.output)
    print("\n✅ 完成！")


if __name__ == "__main__":
    main()
