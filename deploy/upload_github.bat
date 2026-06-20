@echo off
REM ============================================================================
REM  上传到 GitHub (本地终端运行, 不要在 Codex 里执行)
REM  前提: 本机已装 git, 有 GitHub 账号, 已创建空仓库 (不要勾 README/.gitignore/license)
REM ============================================================================
setlocal

if "%REPO_URL%"=="" (
  echo 用法: set REPO_URL=git@github.com:caofeng926/wc-bet-advisor.git ^&^& deploy\upload_github.bat
  echo 或者: set REPO_URL=https://github.com/caofeng926/wc-bet-advisor.git
  echo        deploy\upload_github.bat
  exit /b 1
)

cd /D "%~dp0\.."

echo === [1/5] 检查 git ===
where git >nul 2>nul
if errorlevel 1 (
  echo [X] 未找到 git,先去 https://git-scm.com 下载安装
  exit /b 1
)
git --version

echo === [2/5] git init + 配置 user ===
if not exist .git (
  git init
  git branch -M main
)
if "%GH_USER%"=="" set "GH_USER=wc-bet-deploy"
if "%GH_EMAIL%"=="" set "GH_EMAIL=wc-bet-deploy@local"
git config user.name  "%GH_USER%"
git config user.email "%GH_EMAIL%"

echo === [3/5] 首次全量提交 ===
git add -A
git status --short
git commit -m "feat: 2026 世界杯体彩竞猜购彩建议程序 v0.2.0

- 后端 FastAPI + 8 个模块: matches / admin / lotto / parlay / polymarket / football / slips / recommendations
- 前端 React + Vite + Tailwind: 8 个页面 (Dashboard + 4 个新玩法页 + Champion + 14场 + 串关 + 方案库)
- sporttery.cn API 集成 + ELO/泊松/HTFT/Kelly 模型 + Champion 兜底
- 串关 6 场上限双端校验
- docker-compose 一键起 + deploy/ 一键上 VPS"
if errorlevel 1 (
  echo [X] 提交失败
  exit /b 1
)

echo === [4/5] 设置远端 + 推送 ===
git remote remove origin 2>nul
git remote add origin "%REPO_URL%"
git push -u origin main
if errorlevel 1 (
  echo [X] push 失败,常见原因:
  echo    - 仓库地址错 (HTTPS 需 PAT, SSH 需配 key)
  echo    - 仓库非空 (删 .git 重来或先 git pull --rebase)
  exit /b 1
)

echo === [5/5] 完成 ===
echo 仓库: %REPO_URL%
echo.
echo 下一步 (在服务器上):
echo   cd /opt/wc-bet
echo   git clone %REPO_URL% .
echo   bash deploy/init.sh /opt/wc-bet
endlocal
