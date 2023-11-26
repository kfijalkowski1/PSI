import socket
import sys
import io
import time

socket.settimeout(0.1)

host_address = "z26_z11_server"

if len(sys.argv) < 2:
    print("no port provided, using 8000")
    port = 8000
else:
    port = int(sys.argv[1])

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    frame_id = 1
    while True:
        data = "314159265358979323846264338327950288419716939937510".encode("ascii")
        data_length = len(data)
        data_frame = (
            frame_id.to_bytes(4, "little") + data_length.to_bytes(2, "little") + data
        )

        binary_stream = io.BytesIO()
        binary_stream.write(data_frame)
        binary_stream.seek(0)
        stream_data = binary_stream.read()
        print("Sending message", repr(data), "of length =", data_length)

        success = False

        while not success:
            s.sendto(stream_data, (host_address, port))
            try:
                response = s.recv(1024)

                success = response[4] == 0

                print(
                    "Message id:",
                    int.from_bytes(response[:4], "little"),
                    "Success" if success else "Failed",
                )
            except TimeoutError:
                success = False

        frame_id += 1
        time.sleep(0.1)
