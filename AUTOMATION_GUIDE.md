# AI 视频生成一人公司 - 自动化流程快速指南

## 🚀 一键启动（推荐）

### 完整流程
```bash
# 生成玄幻小说 + 前 5 集短剧脚本 + AI 视频提示词
python auto_pipeline.py --title "我的小说标题" --genre "玄幻" --brief "一句话创意"
```

### 示例命令
```bash
# 示例：生成一部叫"九天神帝"的玄幻小说，改编前 5 集
python auto_pipeline.py --title "九天神帝" --genre "玄幻" --brief "少年偶得神秘传承，从此踏上逆天之路" --episodes 5
```

---

## 📋 分步执行

### 阶段 1：生成小说大纲和开篇
```bash
python auto_pipeline.py --mode novel --title "九天神帝" --genre "玄幻" --chapters 2000
```

**输出：**
- `01_novel_generation/output/novels/九天神帝_世界观设定.md`
- `01_novel_generation/output/novels/九天神帝_主线剧情.md`
- `01_novel_generation/output/novels/九天神帝_第 1 卷大纲.md`
- `01_novel_generation/output/novels/novel_九天神帝_正文_第 1-20 章.md`

### 阶段 2：从小说生成脚本
```bash
python auto_pipeline.py --mode script --novel "01_novel_generation/output/novels/novel_九天神帝_正文_第 1-20 章.md" --episodes 5
```

**输出：**
- `02_script_writer/output/scripts/S01E01_*.md` (5 集脚本)

### 阶段 3：生成 AI 视频提示词
```bash
python auto_pipeline.py --mode prompt --scripts 02_script_writer/output/scripts/S01E*.md
```

**输出：**
- `03_storyboard/output/AI 视频提示词汇总.md`
- `03_storyboard/output/prompts_data.json`

---

## 📁 输出说明

### 小说输出
| 文件 | 说明 | 用途 |
|------|------|------|
| 世界观设定.md | 修炼体系、势力分布、地理格局 | 保持设定一致性 |
| 主线剧情.md | 8-12 卷的大纲，每卷剧情概述 | 长期创作指导 |
| 第 1 卷大纲.md | 第 1 卷每章的详细概述 | 指导前 100-200 章创作 |
| 正文_第 1-20 章.md | 前 20 章完整内容（每章 2000+ 字） | 改编前 5 集短剧 |

### 脚本输出
每集脚本包含：
- 故事梗概
- 角色列表
- 场景列表
- 15-25 个详细分镜
- 每个镜头的 AI 视频提示词（中英文）

### 提示词输出
- **Markdown 格式**：方便人工查看和复制
- **JSON 格式**：方便程序调用或批量处理

---

## ⚙️ 参数说明

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| --title | 小说标题（必需） | - | "九天神帝" |
| --genre | 小说题材 | 玄幻 | "都市"、"悬疑"、"科幻" |
| --brief | 核心创意 | 空 | "少年获得神秘传承" |
| --chapters | 计划总章节 | 2000 | 1000、3000 |
| --episodes | 短剧集数 | 5 | 3、5、10 |
| --mode | 运行模式 | full | novel、script、prompt |
| --novel | 小说文件路径 | - | 用于 script 模式 |
| --scripts | 脚本文件列表 | - | 用于 prompt 模式 |

---

## 🎯 长篇小说创作策略

对于几千章的长篇小说，建议采用以下策略：

### 1. 先规划后写
- 第一步：生成完整世界观和主线大纲
- 第二步：生成第 1 卷详细大纲（前 100-200 章）
- 第三步：生成前 20 章正文（用于短剧改编）

### 2. 边做边扩
- 短剧做到第 5 集时，再生成第 20-40 章
- 保持小说进度领先短剧 10-20 章

### 3. 分卷管理
```
第 1 卷：1-200 章  初入江湖
第 2 卷：201-400 章  宗门风云
第 3 卷：401-600 章  秘境争锋
...
```

---

## 🔧 API 配置

### 方法 1：环境变量（推荐）
```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-xxx

# Linux/Mac
export ANTHROPIC_API_KEY=sk-ant-xxx
```

### 方法 2：配置文件
编辑 `config/api_keys.yaml`：
```yaml
llm:
  claude_api_key: "sk-ant-xxx"
```

---

## 💡 使用技巧

### 1. 测试运行
先跑通流程，再调整参数：
```bash
# 快速测试（只生成 3 集）
python auto_pipeline.py --title "测试小说" --episodes 3
```

### 2. 批量生成
一次生成多集脚本：
```bash
# 生成 10 集脚本（需要至少 20 章小说内容）
python auto_pipeline.py --mode script --novel "xxx.md" --episodes 10
```

### 3. 提示词优化
手动调整生成的提示词：
- 打开 `03_storyboard/output/AI 视频提示词汇总.md`
- 找到对应镜头
- 复制提示词到 AI 视频工具
- 根据生成效果微调提示词

---

## 📊 生产进度追踪

### 小说进度
- [ ] 世界观设定完成
- [ ] 主线大纲完成
- [ ] 第 1 卷大纲完成
- [ ] 第 1-20 章完成
- [ ] 第 21-40 章完成
- [ ] ...

### 短剧进度
- [ ] S01E01 脚本完成
- [ ] S01E01 视频生成完成
- [ ] S01E02 脚本完成
- [ ] S01E02 视频生成完成
- [ ] ...

---

## 🚨 常见问题

### Q: 生成速度慢？
A: 调整每次生成的章节数，或分批次执行。

### Q: 小说内容不够精彩？
A: 在 `--brief` 中提供更详细的创意，或手动修改生成的内容。

### Q: 提示词生成效果不好？
A: 手动优化提示词，添加更多细节描述。

---

## 📞 下一步

1. **配置 API 密钥**
2. **运行一键流程**
3. **检查生成的文件**
4. **开始生成视频**

祝你创作顺利！
