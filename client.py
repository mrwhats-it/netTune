import matplotlib.pyplot as plt
import socket
import time
import pyaudio
import json
import queue
import threading
import socket
import ssl

packets_dropped = 0
bytes_received = 0
start_time = None
underrun_count = 0
stream_finished = False
time_points = []
throughput_points = []
buffer_points = []

BUFFER_SIZE = 2048
q = queue.Queue(maxsize=50)
buf=bytearray()
init_details_dict=dict()

def fetch_init_details(client):
    buffer = ""

    while True:
        buffer += client.recv(1024).decode()

        if "\n" in buffer:
            msg, buffer = buffer.split("\n", 1)
            data = json.loads(msg)
            break
    return data


def read_buf(n):
    global buf, underrun_count
    underrun = False

    while len(buf) < n:
        try:
            chunk = q.get_nowait()
            buf.extend(chunk)
        except queue.Empty:
            underrun = True
            break

    if len(buf) < n:
        if underrun_count == 0:
            print("[WARN] Buffer underrun detected")
        underrun_count += 1
        out = buf + b'\x00' * (n - len(buf))
        buf.clear()
        return bytes(out)

    out = buf[:n]
    buf = buf[n:]
    return bytes(out)


def network_thread(client):
    global bytes_received, start_time, stream_finished, packets_dropped

    start_time = time.time()

    while True:
        try:
            data = client.recv(BUFFER_SIZE)

            if not data:
                print("Stream finished from server")
                stream_finished = True
                break

            bytes_received += len(data)

            # drop oldest packet if buffer is full
            if q.qsize() > 40:   # only drop when buffer is VERY full
                try:
                    q.get_nowait()
                    packets_dropped += 1
                except queue.Empty:
                    pass

            q.put(data)
            
            # track stats
            current_time = time.time() - start_time
            current_throughput = bytes_received / (current_time + 1e-5) / 1024

            time_points.append(current_time)
            throughput_points.append(current_throughput)
            buffer_points.append(q.qsize())

        except Exception as e:
            print("Network error:", e)
            stream_finished = True
            break


def callback(in_data, frame_count, time_info, status):
    global init_details_dict
    try:
        data=read_buf(frame_count*init_details_dict["smplwidth"]*init_details_dict["channels"])
    except:
        data=b'\x00'*(frame_count * init_details_dict["smplwidth"] * init_details_dict["channels"]) # changed value to formula
    return data,pyaudio.paContinue


def main():
    global init_details_dict

    server_port = 8000
    server_ip = "127.0.0.1"

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client = context.wrap_socket(raw_socket, server_hostname="localhost")
    client.connect((server_ip, server_port))
    print("[INFO] Connected to server")

    request = {
    "action": "PLAY",
    "song": "m1.wav"
    }
    client.send((json.dumps(request) + "\n").encode("utf-8"))

    init_details_dict = fetch_init_details(client)

    if init_details_dict.get("status") != "OK":
        print("Error:", init_details_dict.get("message"))
        return

    print(init_details_dict)
    print("[INFO] Streaming Started")
    nt = threading.Thread(target=network_thread, args=(client,), daemon=True)
    nt.start()

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(init_details_dict["smplwidth"]),
                    channels=init_details_dict["channels"],
                    rate=init_details_dict["framerate"],
                    output=True,
                    stream_callback=callback)
    while q.qsize() < 10:
        time.sleep(0.01)
    stream.start_stream()

    try:
        while not stream_finished:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopping client manually...")

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        client.close()

        # stats
        end_time = time.time()
        duration = end_time - start_time if start_time else 1

        throughput = bytes_received / duration / 1024

        print("\n===== Streaming Stats =====")
        print(f"Time: {duration:.2f} sec")
        print(f"Data received: {bytes_received/1024:.2f} KB")
        print(f"Throughput: {throughput:.2f} KB/s")
        print(f"Buffer underruns: {underrun_count}")
        print(f"Packets dropped: {packets_dropped}")
        print("[INFO] Cleanup complete")
        
        # graph
        plt.figure()
        plt.plot(time_points, throughput_points)
        plt.xlabel("Time (s)")
        plt.ylabel("Throughput (KB/s)")
        plt.title("Throughput vs Time")
        plt.grid()
        plt.show()

        plt.figure()
        plt.plot(time_points, buffer_points)
        plt.xlabel("Time (s)")
        plt.ylabel("Buffer Size (Queue Length)")
        plt.title("Buffer Size vs Time")
        plt.grid()
        plt.show()

main()

