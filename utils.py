def detect_protocol(data: bytes) -> str | None:
    """Detects if the request is Minecraft, HTTP, or SOCKS5"""
    if len(data) < 2:
        return None  # Too small to determine

    # Minecraft
    if data[0] in [0xFE, 0x02, 0x10]:
        return "minecraft"
    
    # SOCKS5
    if data[0] == 0x05:
        if len(data) >= 2 + data[1]:
            return "socks5"

    # SOCKS4
    if data[0] == 0x04:
        if len(data) >= 2 + data[1]:
            return "socks4"

    # HTTP Proxy
    if data.startswith(b"CONNECT "):
        return "http_proxy"

    # HTTP Web
    http_methods = [b"GET ", b"POST ", b"PUT ", b"DELETE ", b"HEAD ", b"OPTIONS ", b"TRACE ", b"PATCH "]
    if any(data.startswith(method) for method in http_methods):
        try:
            line = data.decode(errors='ignore').split('\r\n')[0]
            parts = line.split(" ")
            if len(parts) >= 2:
                path = parts[1]
                if path.startswith("http://") or path.startswith("https://"):
                    return "http_proxy"
                else:
                    return "http_web"
        except:
            return None

    return None
