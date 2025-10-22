"""
Connection Pool for TCP/UDP clients
Manages reusable connections for resource efficiency.
"""
import threading
from queue import Queue
from networking.tcp_client import TCPClient
from networking.udp_client import UDPClient

class ConnectionPool:
    def __init__(self, client_class, host, port, pool_size=5, **kwargs):
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        for _ in range(pool_size):
            client = client_class(host, port, **kwargs)
            self.pool.put(client)

    def acquire(self):
        return self.pool.get()

    def release(self, client):
        self.pool.put(client)

    def size(self):
        return self.pool.qsize()
