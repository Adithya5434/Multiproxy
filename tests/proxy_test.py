import requests
import socks
import socket
from urllib3.exceptions import InsecureRequestWarning
import warnings

# Suppress only the single InsecureRequestWarning from urllib3 needed for HTTPS test
warnings.simplefilter('ignore', InsecureRequestWarning)

PROXY_HOST = "localhost"
PROXY_PORT = 1080

TEST_URLS = {
    "HTTP": "http://example.com",
    "HTTPS": "https://example.com"
}

def test_http_proxy(url):
    proxies = {
        "http": f"http://{PROXY_HOST}:{PROXY_PORT}",
        "https": f"http://{PROXY_HOST}:{PROXY_PORT}"
    }
    try:
        r = requests.get(url, proxies=proxies, timeout=5, verify=False)
        print(f"[HTTP PROXY] {url} -> OK ({r.status_code})")
    except Exception as e:
        print(f"[HTTP PROXY] {url} -> ERROR: {e}")

def test_socks_proxy(url, version):
    socks_version = socks.SOCKS5 if version == 5 else socks.SOCKS4

    socks.set_default_proxy(socks_version, PROXY_HOST, PROXY_PORT)
    socket.socket = socks.socksocket
    try:
        r = requests.get(url, timeout=5, verify=False)
        print(f"[SOCKS{version}] {url} -> OK ({r.status_code})")
    except Exception as e:
        print(f"[SOCKS{version}] {url} -> ERROR: {e}")

if __name__ == "__main__":
    for url_type, url in TEST_URLS.items():
        print(f"\n--- Testing {url_type} ---")
        test_http_proxy(url)
        test_socks_proxy(url, version=4)
        test_socks_proxy(url, version=5)
