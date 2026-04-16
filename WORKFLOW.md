# AI 视频生成一人公司 - 全流程文档

## 项目概述

本项目是一个自动化生产系统，实现从小说创作到视频生成的全流程 AI 化，支持系列化短剧的规模化生产。

---

## 完整工作流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI 视频生成一人公司流程                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ① 创意构思 → ② 小说生成 → ③ 分集大纲 → ④ 单集脚本 → ⑤ 分镜描述        │
│                                      ↓                                  │
│  ⑨ 复盘分析 ← ⑧ 发布上线 ← ⑦ 后期合成 ← ⑥ 视频生成 ← 分镜审核          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 各阶段详细说明

### 阶段 1：创意构思

**目标**：确定剧集的核心概念和定位

**产出文件**：`01_novel_generation/output/concept_XXX.md`

**内容包括**：
- 题材类型（玄幻/都市/悬疑/爱情等）
- 目标受众
- 核心卖点
- 预计集数和时长
- 参考作品

---

### 阶段 2：小说生成

**目标**：生成完整的小说文本

**执行脚本**：`01_novel_generation/novel_generator.py`

**流程**：
1. 读取题材设定和核心概念
2. 调用大模型生成角色设定
3. 生成故事大纲（起承转合）
4. 分章节生成正文

**产出文件**：`01_novel_generation/output/novels/novel_完整标题.md`

**小说文件格式**：
```markdown
---
title: "小说标题"
genre: "玄幻"
total_chapters: 100
status: "completed"
created_at: "2026-04-16"
---

## 世界观设定
...

## 主要角色
- 角色 A：性格、背景、特征
- 角色 B：...

## 正文

### 第一章 章节标题
正文内容...

### 第二章 章节标题
正文内容...
```

---

### 阶段 3：分集大纲

**目标**：将小说改编为分集大纲

**执行脚本**：`02_script_writer/episode_outline.py`

**流程**：
1. 读取小说全文
2. 分析故事结构
3. 划分集数（每集 60-90 秒内容）
4. 生成每集的核心事件和悬念点

**产出文件**：`02_script_writer/output/episode_outline_S01.md`

**分集大纲格式**：
```markdown
---
season: 1
total_episodes: 20
novel_source: "novel_XXX.md"
---

## 第 1 集：第一集标题
- 核心事件：...
- 悬念点：...
- 对应小说章节：第 X-X 章

## 第 2 集：第二集标题
...
```

---

### 阶段 4：单集脚本

**目标**：为每集生成详细的视频脚本

**执行脚本**：`02_script_writer/script_writer.py`

**流程**：
1. 读取分集大纲
2. 生成对白和旁白
3. 设计镜头切换
4. 输出标准化脚本

**产出文件**：`02_script_writer/output/scripts/S01E01_标题.md`

**单集脚本格式**：
```markdown
---
season: 1
episode: 1
title: "第一集标题"
duration: "90s"
status: "script_ready"
created_at: "2026-04-16"
---

## 故事梗概
本集主要内容描述（50-100 字）

## 角色列表
- 角色 A：本集出场情况
- 角色 B：本集出场情况

## 场景列表
| 场号 | 场景 | 时间 | 人物 | 情绪 |
|------|------|------|------|------|
| 1    | 办公室 | 日 | 主角 A | 紧张 |
| 2    | 街道 | 夜 | 主角 A,B | 悬疑 |

## 分镜详情

### Scene 1 - 办公室

#### Shot 1.1
- 景别：[特写]
- 内容：主角坐在办公桌前，突然发现抽屉里的神秘信件
- 对白：无
- 音效：纸张摩擦声
- 时长：5s
- AI 提示词：close-up shot, office desk, mysterious letter, dramatic lighting
- 参考图：assets/ref_images/s1e1_shot1.jpg
- 使用工具：可灵
- 生成参数：{duration: 5s, ratio: 16:9}

#### Shot 1.2
- 景别：[中景]
- 内容：...
- 时长：4s

### Scene 2 - 街道
...

## 片尾悬念
描述本集结尾的悬念点...
```

---

### 阶段 5：分镜生成

**目标**：将脚本文字转换为 AI 可理解的视觉描述

**执行脚本**：`03_storyboard/storyboard_generator.py`

**流程**：
1. 解析脚本文件
2. 为每个镜头生成详细的视觉描述
3. 生成参考图提示词
4. 输出分镜文档

**产出文件**：`03_storyboard/output/S01E01_storyboard.md`

---

### 阶段 6：视频生成

**目标**：调用 AI 视频工具生成每个镜头的视频片段

**执行脚本**：`04_video_generation/video_manager.py`

**流程**：
1. 读取分镜文档
2. 根据配置选择生成工具（可灵/即梦/Runway）
3. 批量提交生成任务
4. 轮询任务状态
5. 下载生成的视频片段

**支持的工具**：
| 工具 | 适用场景 | 优势 |
|------|----------|------|
| 可灵 (Kling) | 人物动作、中文场景 | 对中文提示词友好 |
| 即梦 | 短视频、特效 | 生成速度快 |
| Runway | 高质量电影感 | 效果最成熟 |

**产出文件**：`04_video_generation/output/raw_videos/S01E01/shot_*.mp4`

---

### 阶段 7：后期合成

**目标**：将视频片段合成为完整剧集

**执行脚本**：`05_post_production/compositor.py`

**流程**：
1. 按脚本顺序合并视频片段
2. 添加转场效果
3. 添加 AI 配音（TTS）
4. 添加背景音乐和音效
5. 添加字幕

**产出文件**：`05_post_production/output/final_videos/S01E01_final.mp4`

---

### 阶段 8：发布上线

**目标**：发布视频到各平台

**执行脚本**：`06_metadata/publisher.py`（可选自动化）

**流程**：
1. 生成封面图
2. 编写各平台适配的简介
3. 上传视频
4. 记录发布数据

---

### 阶段 9：复盘分析

**目标**：分析每集数据，优化后续内容

**产出文件**：`06_metadata/records/S01/S01E01_record.md`

**记录文件格式**：
```markdown
---
episode: S01E01
title: "第一集标题"
season: 1
episode_number: 1

# 制作状态
script_status: completed
storyboard_status: completed
video_status: completed
post_production_status: completed
publish_status: published

# 视频生成记录
shots:
  shot_1_1:
    status: generated
    tool: kling
    file: raw_videos/S01E01/shot_1_1.mp4
    duration: 5.2s
    generate_time: "2026-04-16 10:05"
    cost: 0.1
  shot_1_2:
    status: generated
    tool: jimeng
    file: raw_videos/S01E01/shot_1_2.mp4
    duration: 4.8s
    generate_time: "2026-04-16 10:08"
    cost: 0.08

# 成本统计
total_cost: 5.20
total_shots: 25
success_rate: 92%

# 发布数据（可选）
platforms:
  douyin:
    views: 10000
    likes: 500
    comments: 50

# 问题记录
- Shot 1.3 生成失败 2 次，原因为提示词包含敏感内容
- 可灵 API 在 14:00-15:00 期间响应慢

# 改进建议
- 优化提示词过滤
- 增加备用 API 账号
---

## 生成日志
- [2026-04-16 09:00] 脚本审核通过
- [2026-04-16 09:30] 分镜生成完成
- [2026-04-16 10:00] 开始视频生成
- [2026-04-16 12:00] 所有视频片段生成完成
- [2026-04-16 14:00] 后期合成完成
- [2026-04-16 15:00] 发布完成
```

---

## 快速开始

### 生成一部新剧的流程

```bash
# 1. 生成小说
python 01_novel_generation/novel_generator.py --genre "玄幻" --title "我的标题"

# 2. 生成分集大纲
python 02_script_writer/episode_outline.py --novel "output/novels/novel_XXX.md" --episodes 20

# 3. 生成单集脚本
python 02_script_writer/script_writer.py --outline "output/episode_outline_S01.md" --episode 1

# 4. 生成分镜
python 03_storyboard/storyboard_generator.py --script "output/scripts/S01E01_*.md"

# 5. 生成视频
python 04_video_generation/video_manager.py --storyboard "output/S01E01_storyboard.md"

# 6. 后期合成
python 05_post_production/compositor.py --episode "S01E01"

# 7. 生成记录
python 06_metadata/record_generator.py --episode "S01E01"
```

---

## 配置文件说明

### config/api_keys.yaml
存储所有 API 密钥（需要自行创建）

### config/project_config.yaml
项目全局配置，包括：
- 默认剧集参数
- 输出路径配置
- 并发限制

### config/tools_config.yaml
各视频工具的详细配置：
- API 端点
- 生成参数
- 重试策略

---

## 注意事项

1. **API 密钥安全**：不要将 api_keys.yaml 提交到 Git
2. **成本控制**：批量生成前确认账户余额
3. **内容合规**：各平台审核标准不同，需注意
4. **备份策略**：定期备份生成的视频文件
