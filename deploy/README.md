# 一键部署到 43.136.175.219

## 你的环境出不去网，Codex 也出不去网,所以部署要在**你自己**的机器上执行。

### 一次性准备
确认本机有 `ssh.exe` (Windows 10+ 自带 OpenSSH 客户端),打开 PowerShell 或 cmd:
```bat
ssh -V
```

### 一键部署
在项目根目录执行:
```bat
deploy\deploy.bat
```

它会:
1. 把整个项目(排除 node_modules/.venv/dist 等)scp 到 `/opt/wc-bet`
2. 把 `init.sh` 推到 `/tmp/init.sh` 并远程执行
3. init.sh 会:
   - 探测 OS(Debian/Ubuntu/CentOS),自动装 Docker + compose plugin
   - 写 `.env`(如不存在)
   - 放行 5173/8000 端口(若启用了 ufw/firewalld)
   - `docker compose build --pull && up -d`
   - 等前端 /health 探活,打印状态

### 部署后访问
- 前端: http://43.136.175.219:5173
- 后端: http://43.136.175.219:8000  (docs: /docs)

### 常用维护命令 (SSH 进服务器后)
```bash
cd /opt/wc-bet
docker compose ps           # 看容器状态
docker compose logs -f     # 实时日志
docker compose restart     # 重启
docker compose down        # 停止(不删数据)
docker compose up -d --build  # 改完代码后重建
```

### 想走域名 + HTTPS?
在服务器 `cd /opt/wc-bet`,加一个 `docker-compose.https.yml`,挂 certbot 或 Caddy 自动续签。给个域名我帮你写。
