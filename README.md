# AI 视频生成一人公司

一个自动化生产系统，实现从小说创作到视频生成的全流程 AI 化。

## 项目结构

```
video_ai_studio/
├── config/                     # 配置文件
├── 01_novel_generation/       # 小说生成模块
├── 02_script_writer/          # 脚本编写模块
├── 03_storyboard/             # 分镜生成模块
├── 04_video_generation/       # 视频生成模块
├── 05_post_production/        # 后期处理模块
├── 06_metadata/               # 元数据管理模块
├── common/                    # 公共模块
├── assets/                    # 素材资源
└── logs/                      # 日志目录
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API 密钥

```bash
# 复制示例配置文件
cp config/api_keys.example.yaml config/api_keys.yaml

# 编辑 api_keys.yaml 填入你的真实密钥
```

### 3. 运行流程

详见 [WORKFLOW.md](WORKFLOW.md)

## 生产流程

1. **小说生成** → 2. **分集大纲** → 3. **单集脚本** → 4. **分镜描述**
   → 5. **视频生成** → 6. **后期合成** → 7. **发布上线**

## 技术栈

- Python 3.10+
- 大模型：Claude / DeepSeek
- 视频工具：可灵 / 即梦 / Runway

## 许可证

MIT License
