import socket
import wave
import time
import sys
import pyaudio
import json
import queue
import threading
import socket


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
    global buf
    while len(buf) < n:
        try:
            chunk = q.get_nowait()
            buf.extend(chunk)
        except queue.Empty:
            break
    if len(buf) < n:
            out = buf + b'\x00' * (n - len(buf))
            buf.clear()
            return bytes(out)

    out = buf[:n]
    buf = buf[n:]
    return bytes(out)


def network_thread(client):
    while True:
        data=client.recv(BUFFER_SIZE)
        if not data:
            break
        q.put(data)


def callback(in_data, frame_count, time_info, status):
    global init_details_dict
    try:
        data=read_buf(frame_count*init_details_dict["smplwidth"]*init_details_dict["channels"])
    except:
        data=b'\x00'*2048
    return data,pyaudio.paContinue


def main():
    global init_details_dict
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_ip = "0.0.0.0"
    server_port = 8000

    client.connect((server_ip, server_port))
    client.send("PLAY m1.wav".encode("utf8"))
    init_details_dict=fetch_init_details(client)
    print(init_details_dict)
    nt = threading.Thread(target=network_thread, args=(client,))
    nt.start()

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(init_details_dict["smplwidth"]),
                    channels=init_details_dict["channels"],
                    rate=init_details_dict["framerate"],
                    output=True,
                    stream_callback=callback)
    
    while stream.is_active():
        time.sleep(0.1)

    stream.close()
    p.terminate()


main()