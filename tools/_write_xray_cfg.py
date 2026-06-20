import json, os
deploy = r"C:\Users\win\Documents\2026世界杯体彩竞猜\deploy"
cfg = {
  "log": {"loglevel": "warning"},
  "assets": {"geoip": "geoip-only-cn-private.dat"},
  "inbounds": [
    {
      "tag": "socks-in",
      "listen": "127.0.0.1",
      "port": 10908,
      "protocol": "socks",
      "settings": {"udp": False},
      "sniffing": {"enabled": False},
    }
  ],
  "outbounds": [
    {
      "tag": "proxy",
      "protocol": "vless",
      "settings": {
        "vnext": [
          {
            "address": "43.160.242.202",
            "port": 8388,
            "users": [
              {"id": "6a7ce2f2-2546-403d-89f2-40ad20342fa0", "encryption": "none", "flow": ""}
            ],
          }
        ]
      },
      "streamSettings": {"network": "tcp", "security": "none"},
    }
  ],
  "routing": {
    "domainStrategy": "AsIs",
    "rules": [{"type": "field", "ip": ["geoip:private"], "outboundTag": "direct"}],
  },
}
path = os.path.join(deploy, "xray-proxy.json")
# Write WITHOUT BOM (utf-8)
with open(path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
print("written", path, os.path.getsize(path), "bytes")

# Sanity: first 3 bytes should be '{' 'n' not BOM
with open(path, "rb") as f:
    head = f.read(4)
print("first bytes:", head[:4])
