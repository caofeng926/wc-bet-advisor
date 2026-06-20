"""Connect through SOCKS5 proxy to test outbound reach."""
import socket, struct, sys

def socks5_connect(socks_host, socks_port, target_host, target_port):
    """Returns a connected socket through SOCKS5 proxy."""
    s = socket.create_connection((socks_host, socks_port), timeout=10)
    s.sendall(b"\x05\x01\x00")  # ver=5, nmethods=1, NO AUTH
    greeting = s.recv(2)
    assert greeting == b"\x05\x00", f"greeting failed: {greeting.hex()}"
    # CONNECT request
    # ATYP=3 (domain), then 1 byte len + domain
    payload = b"\x05\x01\x00\x03" + bytes([len(target_host)]) + target_host.encode() + struct.pack(">H", target_port)
    s.sendall(payload)
    resp = s.recv(10)
    # Skip ATYP-specific response
    if resp[3] == 0x01:  # IPv4
        s.recv(4 + 2)
    elif resp[3] == 0x03:  # domain
        dlen = s.recv(1)[0]
        s.recv(dlen + 2)
    elif resp[3] == 0x04:  # IPv6
        s.recv(16 + 2)
    rep = resp[1]
    if rep != 0:
        raise RuntimeError(f"SOCKS5 CONNECT rep={rep}")
    return s

# Test 1: SSH to 43.136.175.219:22 through SOCKS5
try:
    s = socks5_connect("127.0.0.1", 10808, "43.136.175.219", 22)
    s.settimeout(5)
    # Read SSH banner
    banner = s.recv(64)
    print(f"OK   43.136.175.219:22 via SOCKS5 -> {banner!r}")
    s.close()
except Exception as e:
    print(f"FAIL 43.136.175.219:22 via SOCKS5 -> {type(e).__name__}: {e}")

# Test 2: as a sanity check, just hit 1.1.1.1
try:
    s = socks5_connect("127.0.0.1", 10808, "1.1.1.1", 443)
    print("OK   1.1.1.1:443 via SOCKS5")
    s.close()
except Exception as e:
    print(f"FAIL 1.1.1.1:443 -> {type(e).__name__}: {e}")
