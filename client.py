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

def fetch_init_details(client):
    buffer = ""

    while True:
        buffer += client.recv(1024).decode()

        if "\n" in buffer:
            msg, buffer = buffer.split("\n", 1)
            data = json.loads(msg)
            break
    return data

def main():

    def callback(in_data, frame_count, time_info, status):
        num_bytes=frame_count*init_details_dict["channels"]*init_details_dict["smplwidth"]
        print()
        print(num_bytes,frame_count,init_details_dict["channels"],init_details_dict["smplwidth"])
        print()
        data=client.recv(num_bytes)
        return data, pyaudio.paContinue
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_ip = "127.0.0.1"
    server_port = 8000

    client.connect((server_ip, server_port))
    client.send("PLAY m1.wav".encode("utf8"))
    init_details_dict=fetch_init_details(client)



    p = pyaudio.PyAudio()
    buffer = queue.Queue(maxsize=50)

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