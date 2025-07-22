# 🌀 Multiprotocol Proxy Server

A lightweight Python-based proxy server that supports **SOCKS4**, **SOCKS5**, **HTTP**, and **Minecraft** — all running on a **single port**.

---

## ✨ Features

✅ Supports the following protocols:

- 🌐 **HTTP Proxy**  
- 🧦 **SOCKS4 Proxy**  
- 🧦 **SOCKS5 Proxy** *(TCP only)*  
- 🎮 **Minecraft Proxy** *(only servers with online-mode=false)*

✅ Everything runs on a **single port**, auto-detecting the protocol using packet inspection.  
✅ Bypasses TCPShield plugin (tested on AppleMC).
✅ Easily extensible for more protocols.

---

## 🚀 Usage

```bash
git clone https://github.com/Adithya5434/Multiproxy.git
cd Multiproxy
python main.py
```

## TODO
- Add UDP support for SOCKS5
- Add IPv6 support for SOCKS5
