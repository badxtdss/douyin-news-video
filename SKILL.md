# SKILL.md — douyin-news-video

## 概述

抖音新闻视频全自动制作与发布技能。**JSON 配置驱动，多条新闻合并为一个视频，一键发布。**

## 快速使用

```bash
# 1. 创建配置文件 news_config.json
# 2. 一条命令生成+发布
python scripts/news_video.py --config news_config.json
```

## JSON 配置格式

```json
{
  "title": "今日国际局势5大热点",
  "tags": "国际局势,军事,财经",
  "bgm": "cinematic suspense bgm",
  "output": "./output",
  "publish": true,
  "douyin-title": "抖音标题（可选，默认用title）",
  "douyin-tags": "话题1,话题2（可选，默认用tags）",
  "news": [
    {
      "title": "新闻标题",
      "bullets": ["要点1", "要点2", "要点3"],
      "timeline": ["事件1", "事件2", "事件3"],
      "impact_title": "影响分析标题",
      "impact": ["影响1", "影响2", "影响3"]
    }
  ]
}
```

## 单条新闻结构（3页）

| 页 | 内容 |
|---|---|
| 标题页 | 醒目大字体 + 编号 |
| 要点+时间线 | 核心信息 + 事件脉络 |
| 影响分析 | 经济/市场/社会影响 |

## 多条新闻合并

- 自动生成总封面（"共N条重要新闻"）
- 每条新闻3页（标题/要点+时间线/影响），N条 = 3N+1页
- 合并为一个视频，fade转场
- 一个标题、一组标签、一次发布

## 视频结构示例（5条新闻 = 16页）

```
封面 → #01 标题 → 要点 → 影响 → #02 标题 → 要点 → 影响 → ... → #05 标题 → 要点 → 影响
```

## 多条新闻合并

- 自动生成总封面（"共N条重要新闻"）
- 每条新闻2页，N条 = 2N+1页
- 合并为一个视频，fade转场
- 一个标题、一组标签、一次发布

## 参数说明

| 参数 | 说明 |
|------|------|
| `--config` | JSON配置文件路径（必填） |

### JSON 配置字段

| 字段 | 说明 | 必填 |
|------|------|------|
| title | 合并视频标题 | ✅ |
| tags | 逗号分隔标签 | ✅ |
| bgm | BGM关键词或文件路径 | ❌ |
| output | 输出目录 | ❌ |
| publish | 是否发布到抖音 | ❌ |
| news[].title | 单条新闻标题 | ✅ |
| news[].subtitle | 副标题（标题页显示） | ❌ |
| news[].bullets | 要点列表 | ✅ |
| news[].timeline | 时间线事件 | ❌ |
| news[].impact_title | 影响分析标题 | ❌ |
| news[].impact | 影响分析要点 | ❌ |

## 依赖

- Python 3, ffmpeg, playwright (含 chromium), yt-dlp
- 抖音 Cookie（首次需运行 `scripts/douyin_login.py`）

## License

MIT
