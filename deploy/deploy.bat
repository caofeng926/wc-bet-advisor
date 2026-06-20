@echo off
REM ============================================================================
REM  WC-Bet-Advisor 一键部署脚本 (Windows 本地终端运行)
REM  目标服务器: 43.136.175.219 (root / 2Vbrm5ah)
REM  作用: 把当前项目通过 SFTP 传到服务器，再用 SSH 在服务器上跑 init.sh
REM  前置: 本机有 ssh.exe (Windows 10+ 自带 OpenSSH)
REM ============================================================================
setlocal EnableDelayedExpansion

set "HOST=43.136.175.219"
set "USER=root"
set "PWD=2Vbrm5ah"
set "REMOTE_DIR=/opt/wc-bet"
set "SSH_OPTS=-o StrictHostKeyChecking=no -o UserKnownHostsFile=NUL -o PubkeyAuthentication=no -o PreferredAuthentications=password"

echo === [1/5] 检查本地 ssh ===
where ssh >nul 2>nul
if errorlevel 1 (
  echo [X] 找不到 ssh.exe,请安装 OpenSSH 客户端后重试
  exit /b 1
)
echo [OK] ssh 已就绪

echo === [2/5] 测试连通性 ===
ping -n 2 %HOST% >nul 2>nul
echo (ping 结果仅供参考,不通也继续)

echo === [3/5] 上传项目到 %REMOTE_DIR% (rsync 没有则用 scp) ===
where rsync >nul 2>nul
if not errorlevel 1 (
  echo 使用 rsync 同步 (排除 node_modules / .venv / dist / __pycache__ ...
  rsync -avz --progress ^
    --exclude="node_modules" --exclude=".venv" --exclude="dist" ^
    --exclude="__pycache__" --exclude=".playwright-cli" ^
    --exclude=".pytest_cache" --exclude=".ruff_cache" ^
    --exclude="*.log" --exclude="*.db" --exclude="*.sqlite*" ^
    -e "ssh %SSH_OPTS%" "%CD%/" "%USER%@%HOST%:%REMOTE_DIR%/"
) else (
  echo rsync 不存在,改用纯 SSH + tar 管道
  tar --exclude=node_modules --exclude=.venv --exclude=dist ^
      --exclude=__pycache__ --exclude=.playwright-cli ^
      --exclude=.pytest_cache --exclude=.ruff_cache ^
      --exclude='*.log' --exclude='*.db' --exclude='*.sqlite*' ^
      -czf - . | ssh %SSH_OPTS% %USER%@%HOST% "mkdir -p %REMOTE_DIR% && tar -xzf - -C %REMOTE_DIR%"
)
if errorlevel 1 (
  echo [X] 上传失败,检查网络/凭证
  exit /b 1
)
echo [OK] 上传完成

echo === [4/5] 上传 init.sh 并在远程执行 ===
scp %SSH_OPTS% "%~dp0init.sh" %USER%@%HOST%:/tmp/init.sh
if errorlevel 1 (
  echo [X] scp init.sh 失败
  exit /b 1
)
ssh %SSH_OPTS% %USER%@%HOST% "chmod +x /tmp/init.sh && bash /tmp/init.sh %REMOTE_DIR%"
if errorlevel 1 (
  echo [X] 远程 init.sh 执行失败
  exit /b 1
)

echo === [5/5] 部署完成! ===
echo.
echo 访问地址:
echo   前端: http://%HOST%:5173
echo   后端: http://%HOST%:8000  (docs: /docs)
echo.
echo 后续维护:
echo   SSH: ssh %SSH_OPTS% %USER%@%HOST%
echo   日志: cd %REMOTE_DIR% ^&^& docker compose logs -f
echo   重启: cd %REMOTE_DIR% ^&^& docker compose restart
echo   停止: cd %REMOTE_DIR% ^&^& docker compose down
endlocal
