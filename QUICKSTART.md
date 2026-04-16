# 快速开始指南

## 1. 环境准备

### 安装 Python
确保已安装 Python 3.10 或更高版本：
```bash
python --version
```

### 安装 FFmpeg
FFmpeg 用于视频处理（后期合成必需）：

**Windows:**
```bash
# 使用 choco
choco install ffmpeg

# 或从官网下载 https://ffmpeg.org/download.html
```

**或使用 winget:**
```bash
winget install FFmpeg
```

### 安装依赖
```bash
cd E:/Video_AI
pip install -r requirements.txt
```

---

## 2. 配置 API 密钥

### 复制配置文件
```bash
cp config/api_keys.example.yaml config/api_keys.yaml
```

### 编辑 api_keys.yaml
填入你的真实 API 密钥：

```yaml
llm:
  claude_api_key: "sk-ant-..."  # Anthropic API

video:
  kling_api_key: "your_kling_key"
  jimeng_api_key: "your_jimeng_key"
```

**或使用环境变量（推荐）:**
```bash
set ANTHROPIC_API_KEY=sk-ant-...
set KLING_API_KEY=your_kling_key
set JIMENG_API_KEY=your_jimeng_key
```

---

## 3. 运行完整流程

### 一键生成（测试用）
```bash
python main.py --stage full --title "我的第一部剧" --genre "玄幻" --episodes 3
```

这会生成：
- 1 部小说（前 3 章示例）
- 3 集分集大纲
- 3 集脚本
- 3 集分镜
- （需要 API 密钥才能生成视频）

---

## 4. 分步执行

### 步骤 1：生成小说
```bash
python main.py --stage novel --title "斗罗大陆新传" --genre "玄幻" --brief "少年唐三穿越到新世界..."
```

输出：`01_novel_generation/output/novels/novel_斗罗大陆新传.md`

### 步骤 2：生成分集大纲
```bash
python main.py --stage outline --novel "01_novel_generation/output/novels/novel_斗罗大陆新传.md" --episodes 20
```

输出：`02_script_writer/output/episode_outline_斗罗大陆新传_S01.md`

### 步骤 3：生成单集脚本
```bash
python main.py --stage script --outline "02_script_writer/output/episode_outline_斗罗大陆新传_S01.md" --episode 1
```

输出：`02_script_writer/output/scripts/S01E01_*.md`

### 步骤 4：生成分镜
```bash
python main.py --stage storyboard --script "02_script_writer/output/scripts/S01E01_*.md"
```

输出：`03_storyboard/output/S01E01_storyboard.md`

### 步骤 5：生成视频
```bash
python main.py --stage video --storyboard "03_storyboard/output/S01E01_storyboard.md" --episode 1
```

输出：`04_video_generation/output/raw_videos/S01E01/shot_*.mp4`

### 步骤 6：后期合成
```bash
python main.py --stage composite --episode 1
```

输出：`05_post_production/output/final_videos/S01E01_final.mp4`

### 步骤 7：生成记录
```bash
python main.py --stage record --episode 1 --script "02_script_writer/output/scripts/S01E01_*.md"
```

输出：`06_metadata/records/S01/S01E01_record.md`

---

## 5. 查看流程文档

详细流程说明请查看：
- [WORKFLOW.md](WORKFLOW.md) - 完整工作流程文档

---

## 6. 常见问题

### Q: 没有 API 密钥怎么办？
A: 可以先运行小说生成和脚本生成部分（使用免费的大模型 API），视频生成部分可以手动使用在线工具。

### Q: 视频生成失败？
A: 检查：
1. API 密钥是否正确
2. 网络连接是否正常
3. 账户余额是否充足
4. 查看 `logs/` 目录下的详细日志

### Q: 如何修改提示词风格？
A: 编辑各模块中的提示词模板，或修改 `01_novel_generation/prompts/` 下的文件。

---

## 7. 下一步

1. 先测试完整流程（减少集数）
2. 根据实际情况调整配置
3. 开始你的第一部 AI 短剧！

祝你创作顺利！
