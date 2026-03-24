# 🎬 douyin-news-video

抖音新闻视频全自动制作与发布技能。

**JSON 配置驱动 → 多条新闻合并 → 一键发布抖音**

## 快速开始

```bash
# 1. 安装依赖
pip install playwright yt-dlp
python -m playwright install chromium
brew install ffmpeg

# 2. 登录抖音（首次）
python scripts/douyin_login.py

# 3. 创建配置 & 一键发布
python scripts/news_video.py --config news_config.json
```

## 配置示例

```json
{
  "title": "今日国际5大热点",
  "tags": "国际局势,军事,财经",
  "bgm": "cinematic suspense bgm",
  "publish": true,
  "douyin-title": "抖音标题",
  "douyin-tags": "话题1,话题2",
  "news": [
    {
      "title": "美军82空降师开赴中东",
      "bullets": ["要点1", "要点2"],
      "timeline": ["事件1", "事件2"],
      "impact_title": "军事影响",
      "impact": ["影响1", "影响2"]
    }
  ]
}
```

## 视频结构

每条新闻 2 页（要点+时间线 / 影响分析），多条合并 + 总封面。

```
封面（共N条）→ 新闻1(2页) → 新闻2(2页) → ... → 新闻N(2页)
```

## License

MIT
