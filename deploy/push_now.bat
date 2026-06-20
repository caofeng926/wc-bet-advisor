@echo off
setlocal
set "REPO_URL=https://github.com/caofeng926/wc-bet-advisor.git"
cd /D "%~dp0\.."
if not exist .git (
  git init
  git branch -M main
)
git config user.name "caofeng926"  2>nul
git config user.email "caofeng926@users.noreply.github.com" 2>nul
git remote remove origin 2>nul
git remote add origin "%REPO_URL%"
git add -A
git status --short
echo.
echo ============================================================
echo 准备 push,需要你在弹窗/终端里输入 GitHub 用户名和 PAT token
echo 用户名: caofeng926
echo 密码:   (贴你的 Personal Access Token, 不是 GitHub 密码)
echo ============================================================
echo.
git push -u origin main
endlocal
