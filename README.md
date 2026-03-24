# 🎬 douyin-news-video

抖音新闻视频全自动制作与发布技能。

## 一键完成

**内容生成 → 图文设计 → 视频合成 → 配BGM音乐 → 发布抖音**

## 功能

- 📄 8页图文幻灯片自动生成（封面/突发/人物/要点/警示/评论/金句/告别）
- 🎨 HTML模板化设计，支持自定义样式
- 🎬 ffmpeg合成视频，带fade转场效果
- 🎵 yt-dlp自动搜索下载YouTube BGM
- 📱 Playwright自动化发布到抖音创作者中心
- ⏰ 支持定时发布

## 安装

```bash
# 安装依赖
pip install playwright yt-dlp
python -m playwright install chromium

# macOS
brew install ffmpeg
```

## 使用

### 一键全流程

```bash
python scripts/pipeline.py \
  --title "新闻标题" \
  --subtitle "副标题" \
  --tag "突发新闻" \
  --points "要点1" "要点2" "要点3" \
  --bio "姓名,出生年,籍贯,身份,亮点" \
  --quotes "评论内容:点赞数" \
  --warning "警示文字" \
  --symptoms "症状1" "症状2" \
  --bgm "起风了 纯音乐" \
  --douyin-title "抖音标题" \
  --douyin-tags "话题1,话题2" \
  --publish \
  --output ./output
```

### 分步执行

```bash
# 1. 生成幻灯片
python scripts/create_slides.py --title "标题" --output ./output

# 2. 合成视频+配乐
python scripts/make_video.py --slides ./output --bgm "音乐关键词" --output ./output/final.mp4

# 3. 发布抖音
python scripts/douyin_publish.py --video ./output/final.mp4 --title "标题" --tags "话题"
```

### 抖音登录

首次使用需要扫码登录：

```bash
python scripts/douyin_login.py
```

## 视频规格

- 分辨率：1080 × 1440（抖音竖版 3:4）
- 编码：H.264 + AAC
- 帧率：30fps
- 每页停留：4秒
- 转场：fade 淡入淡出 0.8秒
- BGM：自动淡入淡出

## License

MIT
