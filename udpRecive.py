import socket

UDP_IP = ""
UDP_PORT = 1234

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening on UDP {UDP_PORT}...")

while True:
    data, addr = sock.recvfrom(2048)  # Buffer größer als Chunk
    print(f"Received {len(data)} bytes from {addr}")