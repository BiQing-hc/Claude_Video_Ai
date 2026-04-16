# AI 视频生成一人公司 - 项目总览

> 从小说到视频的完整自动化生产系统

---

## 📁 项目结构

```
E:\Video_AI\
│
├── 📘 文档
│   ├── README.md                    # 项目说明
│   ├── QUICKSTART.md                # 快速开始
│   ├── AUTOMATION_GUIDE.md          # 自动化指南
│   ├── WORKFLOW.md                  # 详细流程
│   └── config/API_SETUP.md          # API 配置说明
│
├── ⚙️ 配置
│   ├── config/
│   │   ├── project_config.yaml      # 项目配置
│   │   ├── api_keys.example.yaml    # API 密钥模板
│   │   └── API_SETUP.md             # 配置说明
│   ├── requirements.txt             # Python 依赖
│   └── .gitignore                   # Git 忽略
│
├── 🤖 自动化脚本
│   ├── auto_pipeline.py             # 一键启动主程序
│   │
│   ├── common/                      # 公共模块
│   │   ├── llm_client.py            # 大模型客户端
│   │   ├── utils.py                 # 工具函数
│   │   └── logging_config.py        # 日志配置
│   │
│   ├── 01_novel_generation/         # 小说生成
│   │   ├── novel_generator.py       # 小说生成器
│   │   └── novel_outline_generator.py  # 大纲生成器 ⭐
│   │
│   ├── 02_script_writer/            # 脚本编写
│   │   ├── episode_outline.py       # 分集大纲
│   │   ├── script_writer.py         # 单集脚本
│   │   └── batch_script_writer.py   # 批量生成 ⭐
│   │
│   ├── 03_storyboard/               # 分镜生成
│   │   ├── storyboard_generator.py  # 分镜生成器
│   │   └── batch_storyboard_generator.py  # 批量生成 ⭐
│   │
│   ├── 04_video_generation/         # 视频生成
│   │   ├── generators/
│   │   │   ├── kling_generator.py   # 可灵 AI
│   │   │   └── jimeng_generator.py  # 即梦 AI
│   │   └── video_manager.py         # 统一管理
│   │
│   ├── 05_post_production/          # 后期处理
│   │   └── compositor.py            # 视频合成
│   │
│   └── 06_metadata/                 # 元数据
│       └── record_generator.py      # 记录生成
│
└── 📤 输出目录
    ├── 01_novel_generation/output/novels/      # 小说
    ├── 02_script_writer/output/scripts/        # 脚本
    ├── 03_storyboard/output/                   # 分镜
    ├── 04_video_generation/output/raw_videos/  # 原始视频
    ├── 05_post_production/output/final_videos/ # 成品视频
    └── 06_metadata/records/                    # 制作记录
```

---

## 🚀 快速开始

### 30 秒启动
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API 密钥
# 编辑 config/api_keys.yaml 或设置环境变量

# 3. 一键运行
python auto_pipeline.py --title "我的小说" --genre "玄幻" --episodes 5
```

### 输出内容
- ✅ 小说世界观设定
- ✅ 小说主线大纲
- ✅ 小说前 20 章正文
- ✅ 5 集短剧脚本
- ✅ AI 视频提示词汇总

---

## 📊 生产流程

```
┌─────────────────────────────────────────────────────────────────┐
│                     自动化生产流程                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ① 输入创意                                                     │
│     ↓                                                           │
│  ② 自动生成小说大纲 + 前 20 章                                     │
│     ↓                                                           │
│  ③ 批量生成 5 集短剧脚本                                          │
│     ↓                                                           │
│  ④ 生成 AI 视频提示词                                              │
│     ↓                                                           │
│  ⑤ 手动/自动 生成视频（可灵/即梦）                                 │
│     ↓                                                           │
│  ⑥ 后期合成 + 发布                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 长篇小说策略

### 几千章的小说如何管理？

**分阶段生成：**

| 阶段 | 内容 | 用途 |
|------|------|------|
| 第 1 步 | 世界观 + 主线大纲 | 整体规划 |
| 第 2 步 | 第 1 卷详细大纲（1-200 章） | 指导创作 |
| 第 3 步 | 前 20 章正文 | 改编前 5 集短剧 |
| 第 4 步 | 第 21-40 章正文 | 改编第 6-10 集 |
| ... | 继续生成 | 持续创作 |

**短剧改编比例：**
- 每 2-4 章小说 → 1 集短剧（90 秒）
- 前 20 章 → 前 5 集短剧
- 前 100 章 → 前 25 集短剧

---

## 🛠️ 核心工具

### 1. 一键启动
```bash
python auto_pipeline.py --title "小说名" --episodes 5
```

### 2. 分步执行
```bash
# 只生成小说
python auto_pipeline.py --mode novel --title "xxx"

# 只生成脚本
python auto_pipeline.py --mode script --novel "xxx.md"

# 只生成提示词
python auto_pipeline.py --mode prompt --scripts S01E*.md
```

### 3. 批量工具
- `novel_outline_generator.py` - 小说大纲
- `batch_script_writer.py` - 批量脚本
- `batch_storyboard_generator.py` - 批量提示词

---

## 📝 文档导航

| 文档 | 用途 | 适合人群 |
|------|------|----------|
| **QUICKSTART.md** | 5 分钟快速上手 | 新手 |
| **AUTOMATION_GUIDE.md** | 自动化流程详解 | 开发者 |
| **WORKFLOW.md** | 完整工作流程 | 所有人 |
| **config/API_SETUP.md** | API 配置说明 | 所有人 |
| **README.md** | 项目概述 | 第一次访问 |

---

## 💡 使用场景

### 场景 1：快速验证创意
```bash
# 用小成本验证一个创意
python auto_pipeline.py --title "测试" --episodes 3
# 生成 3 集脚本，手动生成视频看效果
```

### 场景 2：系列化生产
```bash
# 第 1 周：生成前 20 章 + 前 5 集
python auto_pipeline.py --title "长篇" --episodes 5

# 第 2 周：生成第 21-40 章 + 第 6-10 集
python auto_pipeline.py --mode script --novel "..." --episodes 5
```

### 场景 3：批量提示词优化
```bash
# 手动优化提示词后，重新生成汇总
python auto_pipeline.py --mode prompt --scripts S01E*.md
```

---

## 🔧 依赖说明

### 核心依赖
- Python 3.10+
- requests - HTTP 请求
- pyyaml - YAML 配置
- loguru - 日志
- anthropic / openai - 大模型 API

### 可选依赖
- ffmpeg - 视频处理
- moviepy - 视频编辑

### 安装
```bash
pip install -r requirements.txt
```

---

## 📈 后续规划

### 已实现 ✅
- [x] 小说大纲生成
- [x] 批量脚本生成
- [x] 批量提示词生成
- [x] 一键启动流程

### 待实现 🚧
- [ ] 视频生成自动化（需要 API）
- [ ] 自动配音（TTS 集成）
- [ ] 自动字幕生成
- [ ] 自动发布到平台
- [ ] 数据看板（播放量、成本等）

---

## ❓ 常见问题

**Q: 需要配置 API 才能用吗？**
A: 是的，至少需要配置一个大模型 API（Claude/DeepSeek/OpenAI）。

**Q: 生成的小说质量如何？**
A: 取决于使用的模型和提示词。建议人工审核和修改。

**Q: 可以生成多少章？**
A: 理论上无限。建议分批次生成，每次 20-50 章。

**Q: 短剧可以做多少集？**
A: 取决于小说内容。前 20 章可改编 5 集，100 章可改编 25 集。

**Q: 视频生成是自动的吗？**
A: 目前需要手动操作 AI 视频工具（可灵/即梦），后续会集成自动化。

---

## 📞 支持

遇到问题？
1. 查看 `AUTOMATION_GUIDE.md`
2. 查看 `config/API_SETUP.md`
3. 检查日志文件 `logs/`

---

**祝你创作顺利！🎉**
