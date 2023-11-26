import socket
import sys
import io
import time
import math

HOST = 'z26_z11_server'  # The server's hostname or IP address
size = 1
binary_stream = io.BytesIO()

if  len(sys.argv) < 2:
  print("no port, using 8000")
  port=8000
else:
  port = int( sys.argv[1] )

print("Will send to ", HOST, ":", port)


frame_id = 2

def send_msg(msg_length):
  global frame_id
  data = "".join(["x" for x in range(msg_length)]).encode('ascii')
  data_length = len(data)
  data_frame = frame_id.to_bytes(4, 'little') + data_length.to_bytes(2, 'little') + data
  binary_stream = io.BytesIO()
  binary_stream.write(data_frame)
  binary_stream.seek(0)
  stream_data = binary_stream.read()
  print("Message length ", repr(msg_length), " with length = ", data_length)
  s.sendto(stream_data, (HOST, port))
  response = s.recv(1024)
  frame_id += 1
  return response


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
  last_working = 0
  last_not_working = 0
  cur_length = 1
  stop = False

  # just coz
  send_msg(int(cur_length))

  # looking for too big value
  while True:
    response = send_msg(int(cur_length))[4]
    print("response: ", response)
    if response == 0:
      last_working = cur_length
    else:
      last_not_working = cur_length
      break
    cur_length = cur_length * 2

  # narrowing down the value
  while (last_not_working - last_working) >= 1:
    cur_length = (last_not_working + last_working) / 2
    response = send_msg(round(cur_length))[4]
    if response == 0:
      last_working = cur_length
    else:
      last_not_working = cur_length

  print(f"Result: {round(cur_length)}")


print('Client finished.')
