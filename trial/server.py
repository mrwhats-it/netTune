"""PyAudio Example: Play a wave file (callback version)."""

import wave
import time
import sys

import pyaudio

import socket
from streaming.streamer import *
from streaming.music_manager import *

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



def run_server():
    global server

    server_ip = "127.0.0.1"
    port = 8000

    
    server.bind((server_ip, port))
    
    server.listen(0)
    print(f"Listening on {server_ip}:{port}")

    # accept incoming connections
    client_socket, client_address = server.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")

    request = client_socket.recv(1024)
    request = request.decode("utf-8")
    start_stream()

def start_stream(client_socket):
    
    if len(sys.argv) < 2:
        print(f'Plays a wave file. Usage: {sys.argv[0]} filename.wav')
        sys.exit(-1)

    with wave.open(sys.argv[1], 'rb') as wf:
        def callback(in_data, frame_count, time_info, status):
            data = wf.readframes(frame_count)
            client_socket.send(data)
            return (data, pyaudio.paContinue)

        # Instantiate PyAudio and initialize PortAudio system resources (2)
        p = pyaudio.PyAudio()

        # Open stream using callback (3)
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        input=True,
                        stream_callback=callback)

        # Wait for stream to finish (4)
        while stream.is_active():
            time.sleep(0.1)

        # Close the stream (5)
        stream.close()

        # Release PortAudio system resources (6)
        p.terminate()