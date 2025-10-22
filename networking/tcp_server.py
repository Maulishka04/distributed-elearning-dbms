"""
TCP Server for inter-node communication with SSL/TLS
"""
import socket
import ssl
import threading
from typing import Callable

class TCPServer:
    def __init__(self, host: str, port: int, handler: Callable[[socket.socket, tuple], None], certfile: str, keyfile: str, max_connections: int = 10):
        self.host = host
        self.port = port
        self.handler = handler
        self.certfile = certfile
        self.keyfile = keyfile
        self.max_connections = max_connections
        self.server_socket = None
        self.threads = []

    def start(self):
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.max_connections)
        print(f"TCP SSL Server listening on {self.host}:{self.port}")
        while True:
            client_sock, addr = self.server_socket.accept()
            ssl_sock = context.wrap_socket(client_sock, server_side=True)
            t = threading.Thread(target=self.handler, args=(ssl_sock, addr))
            t.start()
            self.threads.append(t)

    def stop(self):
        if self.server_socket:
            self.server_socket.close()
        for t in self.threads:
            t.join()
