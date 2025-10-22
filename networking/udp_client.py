"""
UDP Client for lightweight message communication
"""
import socket
from typing import Optional

class UDPClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message: str) -> Optional[str]:
        self.client_socket.sendto(message.encode(), (self.host, self.port))
        try:
            self.client_socket.settimeout(2)
            data, _ = self.client_socket.recvfrom(4096)
            return data.decode()
        except socket.timeout:
            return None
