# INTERNAL PORTS
# Port on which minecraft is running
MC_SERVER_PORT = 25565

# Minecraft ip on which minecraft is running
MC_SERVER_IP = "localhost"

# SOCKS
# username and password for socks5 leave empty to connect without credentials
SOCKS5_USERNAME = ""
SOCKS5_PASSWORD = ""

# username for socks4 leave empty to connect without credentials
SOCKS4_USERNAME = ""


# static webpapes: 
# structure- {"port":"path"}
# example: {"8888":"templates/index.html", "9999":"templates/xyz.html"}
# don't use ports which are already used by other services
STATIC_WEBPAGES_PORTS = {}


# EXTERNAL PORTS
# IP on which this server listens
LISTEN_IP = "0.0.0.0"

# Main port on which this server listens
LISTEN_PORT = 8080  
