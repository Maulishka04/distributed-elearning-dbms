"""
Sample test code to simulate multiple nodes communicating concurrently
"""
import threading
import time
from networking.tcp_server import TCPServer
from networking.tcp_client import TCPClient
from networking.udp_server import UDPServer
from networking.udp_client import UDPClient
from networking.connection_pool import ConnectionPool

# Dummy SSL certs (use real certs in production)
CERTFILE = "server.crt"
KEYFILE = "server.key"

# TCP handler function
def tcp_handler(sock, addr):
    print(f"TCP connection from {addr}")
    data = sock.recv(4096)
    response = b"ACK: " + data
    sock.sendall(response)
    sock.close()

# UDP handler function
def udp_handler(data, addr, server_socket):
    print(f"UDP message from {addr}: {data.decode()}")
    server_socket.sendto(b"ACK: " + data, addr)

# Start TCP server in a thread
def start_tcp_server():
    server = TCPServer("127.0.0.1", 9001, tcp_handler, CERTFILE, KEYFILE)
    threading.Thread(target=server.start, daemon=True).start()
    return server

# Start UDP server in a thread
def start_udp_server():
    server = UDPServer("127.0.0.1", 9002, udp_handler)
    threading.Thread(target=server.start, daemon=True).start()
    return server

# Simulate multiple TCP clients
def simulate_tcp_clients(n=3):
    pool = ConnectionPool(TCPClient, "127.0.0.1", 9001, pool_size=n, cafile=CERTFILE)
    def client_task(i):
        client = pool.acquire()
        try:
            resp = client.send(f"Hello from TCP client {i}")
            print(f"TCP client {i} got: {resp}")
        finally:
            pool.release(client)
    threads = [threading.Thread(target=client_task, args=(i,)) for i in range(n)]
    for t in threads: t.start()
    for t in threads: t.join()

# Simulate multiple UDP clients
def simulate_udp_clients(n=3):
    pool = ConnectionPool(UDPClient, "127.0.0.1", 9002, pool_size=n)
    def client_task(i):
        client = pool.acquire()
        try:
            resp = client.send(f"Hello from UDP client {i}")
            print(f"UDP client {i} got: {resp}")
        finally:
            pool.release(client)
    threads = [threading.Thread(target=client_task, args=(i,)) for i in range(n)]
    for t in threads: t.start()
    for t in threads: t.join()

if __name__ == "__main__":
    start_tcp_server()
    start_udp_server()
    time.sleep(1)  # Give servers time to start
    simulate_tcp_clients(5)
    simulate_udp_clients(5)
    print("Simulation complete.")
