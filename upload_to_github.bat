@echo off
chcp 65001 >nul
echo ================================================
echo           GitHub 上传脚本
echo ================================================
echo.

REM 检查 git 是否安装
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 git，请先安装 git
    echo 下载地址：https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/6] 初始化 git 仓库...
cd /d "%~dp0"
git init >nul 2>&1
if %errorlevel% equ 0 (
    echo [成功] git 初始化完成
) else (
    echo [警告] 可能已经初始化过了
)

echo.
echo [2/6] 添加文件到暂存区...
git add .
if %errorlevel% equ 0 (
    echo [成功] 文件添加完成
) else (
    echo [错误] 文件添加失败
    pause
    exit /b 1
)

echo.
echo [3/6] 创建提交...
git commit -m "Initial commit: AI 视频生成一人公司项目"
if %errorlevel% equ 0 (
    echo [成功] 提交完成
) else (
    echo [警告] 可能没有更改的文件
)

echo.
echo [4/6] 设置主分支...
git branch -M main
if %errorlevel% equ 0 (
    echo [成功] 主分支设置完成
) else (
    echo [警告] 分支可能已经设置过了
)

echo.
echo [5/6] 配置远程仓库
echo.
echo 请在 GitHub 上创建仓库后，输入仓库地址：
echo 格式：https://github.com/你的用户名/仓库名.git
echo.
set /p REPO_URL="输入仓库地址（或按回车跳过）: "

if not "%REPO_URL%"=="" (
    git remote add origin %REPO_URL% >nul 2>&1
    if %errorlevel% equ 0 (
        echo [成功] 远程仓库配置完成
    ) else (
        echo [警告] 远程仓库可能已经配置过了
        git remote set-url origin %REPO_URL%
    )

    echo.
    echo [6/6] 上传到 GitHub...
    git push -u origin main
    if %errorlevel% equ 0 (
        echo.
        echo ================================================
        echo           上传成功！
        echo ================================================
        echo.
        echo 仓库地址：%REPO_URL%
        echo.
    ) else (
        echo.
        echo ================================================
        echo           上传失败
        echo ================================================
        echo.
        echo 可能的原因：
        echo 1. 网络连接问题
        echo 2. 需要 GitHub 认证（用户名/密码或 Token）
        echo 3. 仓库地址错误
        echo.
        echo 解决方法：
        echo 1. 检查网络连接
        echo 2. 使用 GitHub Token 代替密码
        echo 3. 手动执行：git push -u origin main
        echo.
    )
) else (
    echo.
    echo ================================================
    echo           本地仓库已创建
    echo ================================================
    echo.
    echo 仓库已初始化，但未关联远程仓库
    echo.
    echo 后续手动上传：
    echo   1. 在 GitHub 上创建私有仓库
    echo   2. 执行：git remote add origin https://github.com/你的用户名/仓库名.git
    echo   3. 执行：git push -u origin main
    echo.
)

echo 按任意键退出...
pause >nul
exit /b 0
