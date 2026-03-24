---
name: douyin-news-video
description: 抖音新闻视频全自动制作与发布技能。输入新闻标题+要点，自动生成8页图文幻灯片 → 合成视频 → 配BGM音乐 → 发布到抖音。适用于热点新闻、突发事件、人物报道等短视频制作。
---

# 抖音新闻视频全自动制作与发布

一键完成：内容生成 → 图文设计 → 视频合成 → 配乐 → 发布抖音

## 使用场景

- 用户说"做一条抖音新闻"、"把这个做成抖音视频"
- 用户提供新闻标题和要点，需要快速产出短视频
- 热点事件需要快速响应发布
- 用户说"发抖音"、"自动发布"

## 前置条件

### 依赖安装

```bash
# Python 依赖
pip install playwright
python -m playwright install chromium

# 系统依赖（macOS）
brew install ffmpeg

# YouTube 音乐下载
pip install yt-dlp
```

### 抖音登录（首次）

```bash
python ~/.openclaw/skills/douyin-news-video/scripts/douyin_login.py
```

执行后浏览器弹出二维码，用抖音APP扫码登录，Cookie 自动保存。

检查登录状态：
```bash
python ~/.openclaw/skills/douyin-news-video/scripts/douyin_check.py
```

## 完整工作流

### 方式一：分步执行

```bash
# 第1步：生成幻灯片HTML + 截图PNG
python ~/.openclaw/skills/douyin-news-video/scripts/create_slides.py \
  --title "张雪峰去世" \
  --subtitle "年仅41岁" \
  --tag "突发新闻" \
  --points "多方消息证实" "心源性猝死" "全网哀悼" \
  --bio "张雪峰,1984,黑龙江齐齐哈尔,考研名师,全网粉丝超5000万" \
  --quotes "前两天还看他直播呢:6.4万" "太突然了,不愿意相信:1.5万" \
  --warning "心源性猝死黄金抢救时间仅4分钟" \
  --symptoms "胸闷胸痛" "心悸心跳加速" "不明原因极度疲劳" "头晕眼前发黑" \
  --output ./output_news

# 第2步：幻灯片合成视频 + 配乐
python ~/.openclaw/skills/douyin-news-video/scripts/make_video.py \
  --slides ./output_news \
  --bgm "起风了 纯音乐" \
  --duration 28 \
  --output ./output_news/final.mp4

# 第3步：发布到抖音
python ~/.openclaw/skills/douyin-news-video/scripts/douyin_publish.py \
  --video ./output_news/final.mp4 \
  --title "张雪峰去世 年仅41岁 心源性猝死给所有人敲响警钟" \
  --tags "张雪峰去世,张雪峰,考研,心源性猝死,健康第一"
```

### 方式二：一键全流程

```bash
python ~/.openclaw/skills/douyin-news-video/scripts/pipeline.py \
  --title "张雪峰去世" \
  --subtitle "年仅41岁" \
  --tag "突发新闻" \
  --points "多方消息证实" "心源性猝死" "全网哀悼" \
  --bio "张雪峰,1984,黑龙江齐齐哈尔,考研名师,全网粉丝超5000万" \
  --quotes "前两天还看他直播呢:6.4万" "太突然了,不愿意相信:1.5万" \
  --warning "心源性猝死黄金抢救时间仅4分钟" \
  --symptoms "胸闷胸痛" "心悸心跳加速" "不明原因极度疲劳" "头晕眼前发黑" \
  --bgm "起风了 纯音乐" \
  --douyin-title "张雪峰去世 年仅41岁 心源性猝死给所有人敲响警钟" \
  --douyin-tags "张雪峰去世,张雪峰,考研,心源性猝死,健康第一" \
  --publish \
  --output ./output_news
```

## 参数说明

| 参数 | 说明 | 必填 |
|------|------|------|
| `--title` | 新闻主标题 | ✅ |
| `--subtitle` | 副标题/关键数字 | ❌ |
| `--tag` | 左上角标签（如"突发新闻"） | ❌ |
| `--points` | 要点列表（空格分隔多个） | ❌ |
| `--bio` | 人物信息：姓名,出生年,籍贯,身份,亮点 | ❌ |
| `--quotes` | 网友评论：内容:点赞数（空格分隔多个） | ❌ |
| `--warning` | 警示信息（大字展示） | ❌ |
| `--symptoms` | 症状/要点列表 | ❌ |
| `--bgm` | 背景音乐关键词（自动搜索下载） | ❌ |
| `--duration` | 视频时长（秒，默认28） | ❌ |
| `--publish` | 是否自动发布到抖音 | ❌ |
| `--douyin-title` | 抖音发布标题（最多30字） | 发布时必填 |
| `--douyin-tags` | 抖音话题标签（逗号分隔） | ❌ |
| `--schedule` | 定时发布时间（YYYY-MM-DD HH:MM） | ❌ |
| `--output` | 输出目录 | ❌ |

## 视频结构（8页）

| 页码 | 内容 | 说明 |
|------|------|------|
| 1 | 封面 | 主标题 + 副标题 + 日期 |
| 2 | 突发消息 | 事件概述 + 热搜标签 |
| 3 | 人物介绍 | 信息卡片网格 |
| 4 | 贡献盘点 | 要点列表 + 引用 |
| 5 | 关键信息 | 警示框 + 症状列表 |
| 6 | 网友评论 | 评论卡片 + 点赞数 |
| 7 | 警示金句 | 大字金句页 |
| 8 | 告别页 | 蜡烛 + 年份 |

## 自定义模板

幻灯片 HTML 模板位于 `templates/` 目录：

```
~/.openclaw/skills/douyin-news-video/templates/
├── slide_cover.html      # 封面
├── slide_breaking.html   # 突发消息
├── slide_bio.html        # 人物介绍
├── slide_points.html     # 要点盘点
├── slide_warning.html    # 警示信息
├── slide_comments.html   # 网友评论
├── slide_quote.html      # 金句页
└── slide_farewell.html   # 告别页
```

修改模板可自定义样式（颜色、字体、布局）。

## 视频规格

- 分辨率：1080 x 1440（抖音竖版 3:4）
- 编码：H.264 + AAC
- 帧率：30fps
- 每页停留：4秒（封面/告别 5秒）
- 转场：fade 淡入淡出 0.8秒
- BGM：自动淡入淡出，音量 50%

## 注意事项

1. **Cookie 有效期**：长期未用需重新扫码登录
2. **发布频率**：建议间隔几分钟，避免触发风控
3. **标题限制**：抖音标题最多30字
4. **BGM 版权**：使用 YouTube 音乐可能有版权风险，建议使用无版权音乐
5. **审核时间**：发布后需等待抖音审核通过

## 目录结构

```
~/.openclaw/skills/douyin-news-video/
├── SKILL.md                    # 技能说明
├── scripts/
│   ├── pipeline.py             # 一键全流程
│   ├── create_slides.py        # 生成幻灯片
│   ├── make_video.py           # 合成视频+配乐
│   ├── douyin_publish.py       # 抖音发布
│   ├── douyin_login.py         # 抖音登录
│   └── douyin_check.py         # 登录状态检查
├── templates/
│   └── *.html                  # 幻灯片模板
└── cookies/
    └── douyin.json             # 登录Cookie
```
