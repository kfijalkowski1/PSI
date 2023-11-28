import socket
import sys
import io
import time

host_address = "z26_z13_server"

RED = "\033[0;31m"
CLEAR = "\033[0m"

if len(sys.argv) < 2:
    print("no port provided, using 8000")
    port = 8000
else:
    port = int(sys.argv[1])

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.settimeout(0.1)
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
                matching_id = False
                while not matching_id:
                    response = s.recv(1024)

                    response_id = int.from_bytes(response[:4], "little")

                    if response_id == frame_id:
                        success = response[4] == 0
                        matching_id = True

                print(
                    "Message id:",
                    response_id,
                    "Success" if success else f"{RED}Failed{CLEAR}",
                )
            except TimeoutError:
                success = False
                print(f"{RED}Response timeout{CLEAR}")

            time.sleep(0.3)

        frame_id += 1
        time.sleep(1)
