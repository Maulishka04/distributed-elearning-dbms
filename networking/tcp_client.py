"""
TCP Client for inter-node communication with SSL/TLS
"""
import socket
import ssl
from typing import Optional

class TCPClient:
    def __init__(self, host: str, port: int, cafile: Optional[str] = None):
        self.host = host
        self.port = port
        self.cafile = cafile

    def send(self, message: str) -> str:
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=self.cafile)
        with socket.create_connection((self.host, self.port)) as sock:
            with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                ssock.sendall(message.encode())
                data = ssock.recv(4096)
                return data.decode()
