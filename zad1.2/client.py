import socket
import sys
import io
import time

HOST = 'z26_z11_server'  # The server's hostname or IP address
size = 1
binary_stream = io.BytesIO()

if  len(sys.argv) < 2:
  print("no port, using 8000")
  port=8000
else:
  port = int( sys.argv[1] )

print("Will send to ", HOST, ":", port)

frame_id = 0

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
  for step in range(10):
    data = "".join(["X" for _ in range(step * 256)]).encode('ascii')
    data_length = len(data)
    data_frame = frame_id.to_bytes(4, 'little') + data_length.to_bytes(2, 'little') + data

    binary_stream = io.BytesIO()
    binary_stream.write(data_frame)
    binary_stream.seek(0)
    stream_data = binary_stream.read()
    print("Sent message with bytes: ", repr(step), " with length = ", data_length)

    s.sendto(stream_data, (HOST, port))
    response = s.recv(1024)

    print('Received', int.from_bytes(response[:4], "little"), "Success" if response[4]==0  else "Failed" )

    frame_id += 1
    time.sleep(0.1)


print('Client finished.')