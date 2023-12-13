import socket
import sys

HOST = "z26_z21_server"  # The server's hostname or IP address

if len(sys.argv) < 2:
    print("no port, using 8000")
    port = 8000
else:
    port = int(sys.argv[1])

print("Will connect to ", HOST, ":", port)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, port))
    #    s.sendall(b'0123456789')
    # what happens when we send more data to server accepting only 10B at a time?
    s.sendall(b"Hello, world!")
    data = s.recv(1024)

print("Received", repr(data))
print("Client finished.")
