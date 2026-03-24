# 🎬 douyin-news-video

抖音新闻视频全自动制作与发布技能。

**智能分析新闻内容 → 自动生成图文 → 合成视频 → 配BGM → 发布抖音**

## ✨ 特性

- 🧠 **智能类型判断** — 根据内容自动识别财经/政治/科技/悼念/体育等类型
- 📄 **8页自适应幻灯片** — 封面/要点/背景/数据卡片/时间线/引用/金句/结尾
- 🎬 **视频自动合成** — ffmpeg fade转场，30fps，1080×1440竖版
- 🎵 **BGM自动匹配** — 根据关键词从YouTube搜索下载纯音乐
- 📱 **一键发布抖音** — Playwright自动化，支持定时发布

## 快速开始

```bash
# 安装依赖
pip install playwright yt-dlp
python -m playwright install chromium
brew install ffmpeg

# 登录抖音（首次）
python scripts/douyin_login.py

# 一键全流程
python scripts/pipeline.py \
  --title "新闻标题" \
  --subtitle "副标题" \
  --bullets "要点1" "要点2" "要点3" \
  --context "背景信息" \
  --data "标签:数值" "标签:数值" \
  --timeline "事件1" "事件2" \
  --quotes "引用内容:来源" \
  --highlight "核心观点" \
  --bgm "音乐关键词" \
  --douyin-title "抖音标题" \
  --douyin-tags "话题1,话题2" \
  --publish \
  --output ./output
```

## 幻灯片模板

| 页码 | 用途 | 说明 |
|------|------|------|
| 1 | 封面 | 标题 + 副标题 + 自动标签 |
| 2 | 要点速览 | 核心信息列表 |
| 3 | 背景梳理 | 事件上下文 |
| 4 | 关键数据 | 数据卡片网格 |
| 5 | 时间线 | 事件发展脉络 |
| 6 | 各方反应 | 引用/评论 |
| 7 | 核心观点 | 金句大字 |
| 8 | 结尾 | 关注引导 |

## License

MIT
