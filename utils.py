def detect_protocol(data: bytes) -> str | None:
    """Detects if the request is Minecraft, HTTP, or SOCKS5"""
    if len(data) < 2:
        return None  # Too small to determine

    # Minecraft
    if is_minecraft_protocol(data):
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
                    return "http_web" # if the ip was opened in a browser
        except:
            return None

    return None


def read_varint(data, offset=0):
    value = 0
    shift = 0
    pos = offset
    while True:
        if pos >= len(data):
            raise ValueError("VarInt extends beyond data length")
        byte = data[pos]
        value |= (byte & 0x7F) << shift
        shift += 7
        pos += 1
        if not (byte & 0x80):
            break
        if shift > 35:
            raise ValueError("VarInt too big")
    return value, pos

def write_varint(value: int) -> bytes:
    result = bytearray()
    while True:
        temp = value & 0x7F  # Take 7 bits
        value >>= 7
        if value != 0:
            temp |= 0x80  # Set continuation bit
        result.append(temp)
        if value == 0:
            break
    return bytes(result)

def is_minecraft_protocol(data):
    try:
        if data[0] in (0xFE, 0x02, 0x10):
            return True
        
        # Read packet length
        _, index = read_varint(data)

        # Read packet ID
        packet_id, index = read_varint(data, index)

        return packet_id == 0x00
    except:
        return False
