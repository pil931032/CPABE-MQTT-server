import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Echo")
    data = s.recv(1024)
    s.close()

data = data.decode("utf-8") 
print(f"Received {data!r}")