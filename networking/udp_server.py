"""
UDP Server for lightweight message communication
"""
import socket
import threading
from typing import Callable

class UDPServer:
    def __init__(self, host: str, port: int, handler: Callable[[bytes, tuple, socket.socket], None]):
        self.host = host
        self.port = port
        self.handler = handler
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.server_socket.bind((self.host, self.port))
        print(f"UDP Server listening on {self.host}:{self.port}")
        self.thread = threading.Thread(target=self._listen)
        self.thread.start()

    def _listen(self):
        while self.running:
            data, addr = self.server_socket.recvfrom(4096)
            self.handler(data, addr, self.server_socket)

    def stop(self):
        self.running = False
        self.server_socket.close()
        if self.thread:
            self.thread.join()
