# GitHub 推送说明

## 当前状态

✅ 本地 git 仓库已创建
✅ 文件已添加到暂存区
✅ 第一个提交已创建（39 个文件）
✅ 远程仓库已关联：`https://github.com/BiQing-hc/Claude_Video_Ai.git`
❌ 网络推送失败（需要检查网络/代理）

---

## 手动推送步骤

### 方法 1：直接使用命令行

打开 PowerShell 或 CMD，执行：

```bash
cd E:\Video_AI

# 设置分支名称
git branch -M main

# 推送到 GitHub（会提示输入用户名和密码）
git push -u origin main
```

**如果提示认证失败**，使用 GitHub Token：

```bash
# 使用 Token 代替密码
git push https://你的用户名:你的Token@github.com/BiQing-hc/Claude_Video_Ai.git main
```

---

### 方法 2：使用 GitHub Desktop（推荐）

1. 下载 GitHub Desktop: https://desktop.github.com/
2. 安装并登录 GitHub 账号
3. 点击 `File` → `Add Local Repository`
4. 选择 `E:\Video_AI` 文件夹
5. 点击 `Publish repository`
6. 选择私有仓库

---

### 方法 3：使用 GitHub CLI

```bash
# 安装 GitHub CLI
winget install --id GitHub.cli

# 登录
gh auth login

# 推送
gh repo push --force
```

---

## 获取 GitHub Token

1. 访问：https://github.com/settings/tokens
2. 点击 `Generate new token (classic)`
3. 填写备注（如：Video AI Studio）
4. 勾选权限：`repo`（全选）
5. 点击 `Generate token`
6. **复制并保存 Token**（只显示一次）

---

## 网络问题解决

### 如果使用代理：

```bash
# 配置 git 使用代理
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 然后再推送
git push -u origin main

# 推送完成后可取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 如果不使用代理：

检查防火墙设置，确保可以访问 `github.com`

---

## 验证推送成功

1. 访问：https://github.com/BiQing-hc/Claude_Video_Ai
2. 刷新页面
3. 确认文件已上传

---

## 后续更新

```bash
cd E:\Video_AI
git add .
git commit -m "更新说明"
git push
```

---

## 仓库包含的文件

```
Claude_Video_Ai/
├── README.md
├── PROJECT_OVERVIEW.md
├── AUTOMATION_GUIDE.md
├── QUICKSTART.md
├── WORKFLOW.md
├── GITHUB_UPLOAD_GUIDE.md
├── PROJECT_SUMMARY_九天神帝.md
├── requirements.txt
├── .gitignore
├── auto_pipeline.py
├── main.py
├── config/
│   ├── project_config.yaml
│   ├── api_keys.example.yaml
│   └── API_SETUP.md
├── common/
│   ├── llm_client.py
│   ├── utils.py
│   └── logging_config.py
├── 01_novel_generation/
├── 02_script_writer/
├── 03_storyboard/
├── 04_video_generation/
├── 05_post_production/
└── 06_metadata/
```

**注意**：`config/api_keys.yaml` 已在 .gitignore 中，不会被上传。

---

祝你上传成功！
