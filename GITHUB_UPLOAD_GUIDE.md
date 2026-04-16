# GitHub 上传指南

## 快速上传步骤

### 步骤 1：在 GitHub 上创建仓库

1. 登录 https://github.com/
2. 点击右上角 `+` → `New repository`
3. 填写仓库名称，例如：`video-ai-studio`
4. 选择 **Private**（私有仓库）
5. **不要** 勾选 "Initialize this repository with a README"
6. 点击 `Create repository`

### 步骤 2：运行上传命令

打开命令行（PowerShell 或 CMD），依次执行：

```bash
# 进入项目目录
cd /d "E:\Video_AI"

# 初始化 git
git init

# 添加所有文件
git add .

# 创建第一个提交
git commit -m "Initial commit: AI 视频生成一人公司项目

- 小说生成模块
- 脚本生成模块
- 分镜提示词生成模块
- 自动化流程脚本
- 示例小说《九天神帝》1-10 章
- 5 集短剧完整脚本和提示词"

# 关联 GitHub 仓库（替换为你的仓库地址）
git remote add origin https://github.com/你的用户名/video-ai-studio.git

# 上传到 GitHub
git push -u origin main
```

### 步骤 3：验证上传

1. 刷新 GitHub 仓库页面
2. 确认文件已上传成功

---

## 常见问题

### Q: 提示 "Permission denied" 或认证失败？

**解决方法 1：使用 GitHub Token**
```bash
# 在 GitHub 上创建 Token:
# Settings → Developer settings → Personal access tokens → Generate new token

# 然后使用 token 上传
git remote set-url origin https://你的用户名:你的Token@github.com/你的用户名/video-ai-studio.git
git push -u origin main
```

**解决方法 2：安装 Git Credential Manager**
- Windows 用户推荐安装：https://github.com/GitCredentialManager/git-credential-manager

### Q: 提示 "branch main not found"？

```bash
# 使用 master 分支
git branch -M main
git push -u origin main
```

### Q: 文件太大上传失败？

编辑 `.gitignore` 文件，忽略输出目录：
```
# 在 .gitignore 中添加
01_novel_generation/output/
02_script_writer/output/
03_storyboard/output/
04_video_generation/output/
```

然后：
```bash
git rm -r --cached 01_novel_generation/output/
git commit -m "Remove large output files"
git push
```

---

## 后续更新

修改代码后，上传新内容：

```bash
cd /d "E:\Video_AI"
git add .
git commit -m "更新说明"
git push
```

---

## 推荐的仓库结构

上传后，你的仓库应该包含：

```
video-ai-studio/
├── README.md                    # 项目说明
├── PROJECT_OVERVIEW.md          # 项目总览
├── AUTOMATION_GUIDE.md          # 自动化指南
├── requirements.txt             # Python 依赖
├── .gitignore                   # Git 忽略配置
├── auto_pipeline.py             # 一键启动脚本
├── config/                      # 配置文件（不含密钥）
├── common/                      # 公共模块
├── 01_novel_generation/         # 小说生成
├── 02_script_writer/            # 脚本生成
├── 03_storyboard/               # 分镜生成
├── 04_video_generation/         # 视频生成
├── 05_post_production/          # 后期处理
└── 06_metadata/                 # 元数据
```

**注意**：
- `config/api_keys.yaml` 不会被上传（已在 .gitignore 中）
- `output/` 目录的文件可以选择性上传（体积较大）

---

## 安全提示

1. **永远不要** 提交 `api_keys.yaml` 到 GitHub
2. 如果不小心提交了，立即删除并更换 API 密钥
3. 使用环境变量存储敏感信息

---

祝你上传顺利！
