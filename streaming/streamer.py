import os
import time
from protocol import pack_chunk
import struct

CHUNK_SIZE = 4096
MUSIC_FOLDER = "../music"

class StreamState:

    def __init__(self):
        self.paused = False
        self.stopped = False

HEADER_SIZE = 4

def pack_chunk(data):
    size = len(data)
    header = struct.pack("!I", size)
    return header + data

def unpack_header(header_bytes):
    return struct.unpack("!I", header_bytes)[0]

def stream_song(client_socket, song_name, state):
    path = os.path.join(MUSIC_FOLDER, song_name)
    if not os.path.exists(path):
        client_socket.sendall(b"error song not found\n")
        return
    
    print(f"streaming started: {song_name}")
    client_socket.sendall(b"STREAM_START\n")

    try:
        with open(path, "rb") as file:
            while True:
                if state=="STOP":
                    break
            
                if state=="PAUSE":
                    time.sleep(0.1)
                    continue

                chunk = file.read(CHUNK_SIZE)
                if not chunk:
                    break
                
                packet = pack_chunk(chunk)
                client_socket.sendall(packet)
                time.sleep(0.02)
    except Exception as e:
        print("streaming error: ", e)

    print(f"streaming ended")
    client_socket.sendall(b"STREAM_END\n")


def pause_stream(state):
    state.paused = True

def resume_stream(state):
    state.paused = False

def stop_stream(state):
    state.stopped = True

