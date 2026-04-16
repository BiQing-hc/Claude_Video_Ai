# API 密钥配置说明

## 重要提示
⚠️ **切勿将 api_keys.yaml 提交到 Git 或公开分享！**

---

## 配置步骤

### 步骤 1：复制配置文件
```bash
# 在项目根目录执行
cp config/api_keys.example.yaml config/api_keys.yaml
```

### 步骤 2：编辑配置文件
用文本编辑器打开 `config/api_keys.yaml`：

```yaml
# 大模型 API（必需，至少配置一个）
llm:
  claude_api_key: "sk-ant-api03-xxxxxxxxxxxxx"  # Anthropic Claude
  deepseek_api_key: "sk-xxxxxxxxxxxxx"          # 深度求索（国内）
  openai_api_key: "sk-xxxxxxxxxxxxx"            # OpenAI

# 视频生成 API（暂时不需要，后续使用）
video:
  kling_api_key: "your_kling_key"               # 可灵 AI
  jimeng_api_key: "your_jimeng_key"             # 即梦 AI

# 其他服务（可选）
services:
  elevenlabs_api_key: "your_elevenlabs_key"     # TTS 配音
```

### 步骤 3：保存文件
保存后，程序会自动读取配置。

---

## 获取 API 密钥

### 1. Anthropic Claude（推荐）
- 官网：https://console.anthropic.com/
- 需要海外支付方式
- 优点：效果最好，支持中文

### 2. DeepSeek 深度求索（国内推荐）
- 官网：https://platform.deepseek.com/
- 国内可直接使用
- 优点：价格便宜，中文支持好

### 3. OpenAI
- 官网：https://platform.openai.com/
- 需要海外支付方式
- 优点：生态成熟

---

## 使用环境变量（更安全）

### Windows
```cmd
set ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
set DEEPSEEK_API_KEY=sk-xxxxx
```

### Linux/Mac
```bash
export ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
export DEEPSEEK_API_KEY=sk-xxxxx
```

### 永久设置（推荐）
将以下内容添加到系统环境变量：

**Windows:**
1. 右键"此电脑" → 属性 → 高级系统设置
2. 环境变量 → 用户变量 → 新建
3. 变量名：`ANTHROPIC_API_KEY`
4. 变量值：`sk-ant-api03-xxxxx`

**Linux/Mac:**
在 `~/.bashrc` 或 `~/.zshrc` 中添加：
```bash
export ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

---

## 配置文件说明

### config/project_config.yaml
项目全局配置，一般不需要修改：

```yaml
# 默认使用的大模型
llm:
  provider: "claude"     # claude / deepseek / openai
  model: "claude-sonnet-4-6"
  max_tokens: 8192

# 路径配置
paths:
  novels: "01_novel_generation/output/novels"
  scripts: "02_script_writer/output/scripts"
  storyboards: "03_storyboard/output"
  raw_videos: "04_video_generation/output/raw_videos"
  final_videos: "05_post_production/output/final_videos"
  records: "06_metadata/records"
```

---

## 测试配置

运行以下命令测试配置是否正确：

```bash
# 测试小说生成（会消耗少量 token）
python auto_pipeline.py --mode novel --title "测试" --brief "测试创意"
```

如果配置正确，会看到：
```
✅ 小说生成完成
```

如果配置错误，会看到：
```
❌ 未找到 API 密钥
```

---

## 安全提示

1. **不要分享** `config/api_keys.yaml` 文件
2. **不要上传**到 GitHub 等公开仓库
3. 定期**更换密钥**
4. 设置**使用额度限制**

---

## 费用估算

### 小说生成
- 世界观 + 大纲：约 10,000 tokens
- 每章正文（2000 字）：约 3,000 tokens
- 前 20 章总计：约 70,000 tokens

**费用参考：**
- Claude: 约 $0.50 - $1.00
- DeepSeek: 约 ¥1 - ¥2

### 脚本生成
- 每集脚本：约 5,000 tokens
- 5 集结总计：约 25,000 tokens

**费用参考：**
- Claude: 约 $0.20 - $0.40
- DeepSeek: 约 ¥0.5 - ¥1

---

## 故障排除

### 问题：提示"未找到 API 密钥"
**解决：**
1. 检查 `config/api_keys.yaml` 是否存在
2. 检查密钥是否正确复制（包含完整前缀）
3. 重启终端/命令行

### 问题：提示"API 请求失败"
**解决：**
1. 检查网络连接
2. 检查账户余额
3. 检查 API 密钥是否过期

### 问题：生成速度慢
**解决：**
1. 切换到 DeepSeek（国内更快）
2. 减少并发请求数
3. 检查网络代理设置

---

## 联系方式

如有问题，请查看：
- `README.md` - 项目说明
- `QUICKSTART.md` - 快速开始
- `AUTOMATION_GUIDE.md` - 自动化指南
