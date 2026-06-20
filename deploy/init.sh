#!/usr/bin/env bash
# ============================================================================
#  WC-Bet-Advisor 服务器端初始化脚本
#  在远程 root shell 里跑,做以下事:
#    1) 装 Docker + docker-compose plugin(若未装)
#    2) 创建项目目录、改 .env、放行防火墙端口
#    3) docker compose up -d 构建并启动
#    4) 等待 health 通过
#    5) 打印探活结果
# ============================================================================
set -euo pipefail

REMOTE_DIR=""

# ─── 替代方案: 用 git clone 代替 scp 上传 ───────────────────────────────
# 如果你的项目已经在 GitHub (推荐),可以在服务器上跑:
#   cd $REMOTE_DIR && git clone https://github.com/caofeng926/wc-bet-advisor.git .
# 这样不用每次改完都 scp,直接 git pull 就能更新。
HOST_IP="$(curl -s --max-time 5 ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')"

log()  { printf '\n\033[1;36m==>\033[0m %s\n' "$*"; }
warn() { printf '\n\033[1;33m[warn]\033[0m %s\n' "$*"; }
fail() { printf '\n\033[1;31m[fatal]\033[0m %s\n' "$*"; exit 1; }

log "[1/6] 检查系统"
. /etc/os-release 2>/dev/null || true
echo "  OS: ${PRETTY_NAME:-unknown}"
echo "  IP: ${HOST_IP}"

log "[2/6] 检查/安装 Docker"
if ! command -v docker >/dev/null 2>&1; then
  warn "未找到 docker,尝试安装..."
  if command -v apt-get >/dev/null 2>&1; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq
    apt-get install -y -qq ca-certificates curl gnupg
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  elif command -v yum >/dev/null 2>&1; then
    yum install -y -q yum-utils
    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    yum install -y -q docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  else
    fail "无法识别的包管理器,请手动装 docker"
  fi
  systemctl enable --now docker
fi

if ! docker compose version >/dev/null 2>&1; then
  fail "已装 docker 但缺少 compose plugin"
fi

docker --version
docker compose version

log "[3/6] 准备项目目录"
mkdir -p "$REMOTE_DIR"
cd "$REMOTE_DIR"

# 写 .env (如不存在)
if [ ! -f .env ]; then
  cat > .env <<'EOF'
DATABASE_URL=sqlite:///./data/wc_bet.db
CORS_ORIGINS=http://43.136.175.219:5173,http://43.136.175.219:8000
LOG_LEVEL=INFO
FOOTBALL_DATA_API_KEY=
POLYMARKET_API_BASE=https://gamma-api.polymarket.com
ODDS_API_KEY=
EOF
  log "已生成 .env"
fi

# 确保子目录存在
mkdir -p backend/data backend/data/snapshots

log "[4/6] 防火墙放行 (如启用 ufw/firewalld)"
if command -v ufw >/dev/null 2>&1 && ufw status 2>/dev/null | grep -q "Status: active"; then
  ufw allow 5173/tcp comment 'wc-bet-frontend'
  ufw allow 8000/tcp comment 'wc-bet-backend' || true
elif command -v firewall-cmd >/dev/null 2>&1 && systemctl is-active --quiet firewalld; then
  firewall-cmd --permanent --add-port=5173/tcp
  firewall-cmd --permanent --add-port=8000/tcp || true
  firewall-cmd --reload
fi

log "[5/6] docker compose build + up"
docker compose build --pull
docker compose up -d

log "[6/6] 等服务就绪 (最多 90s)"
for i in $(seq 1 30); do
  if curl -s --max-time 3 http://127.0.0.1:5173/ >/dev/null 2>&1; then
    ok_front=1; break
  fi
  sleep 3
done
for i in $(seq 1 30); do
  if curl -s --max-time 3 http://127.0.0.1:8000/health | grep -q '"ok"'; then
    ok_back=1; break
  fi
  sleep 3
done

echo
echo "==================== 部署状态 ===================="
docker compose ps
echo "=================================================="
[ -n "${ok_front:-}" ] && echo "前端  http://$HOST_IP:5173  ✓" || echo "前端  http://$HOST_IP:5173  ✗ 未就绪"
[ -n "${ok_back:-}" ]  && echo "后端  http://$HOST_IP:8000  ✓" || echo "后端  http://$HOST_IP:8000  ✗ 未就绪"
echo
echo "如需排错: cd $REMOTE_DIR && docker compose logs -f --tail=200"
