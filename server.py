import socket
from streaming.streamer import *
from streaming.music_manager import *
import wave
import json
import threading

MUSIC_FOLDER = "music"
BUFFER_SIZE = 2048

def init_details(client_socket,song_name):
    
    path = os.path.join(MUSIC_FOLDER, song_name)
    with wave.open(path, 'rb') as wf:
        details={"smplwidth":wf.getsampwidth(),
                 "channels":wf.getnchannels(),
                 "framerate":wf.getframerate()}
        
        client_socket.send((json.dumps(details) + "\n").encode())
        return details

def read_data(client_socket,song_name):
    path = os.path.join(MUSIC_FOLDER, song_name)
    with wave.open(path, 'rb') as wf:
        while True:
            data=wf.readframes(1024)
            if data==b'':
                break
            client_socket.sendall(data)

def run_client(client_socket,client_address):
    instruction=client_socket.recv(BUFFER_SIZE).decode("utf8")
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
    
    #for now just take the filename
    song_name=instruction.split()[1]

    details=init_details(client_socket,song_name)
    read_data(client_socket,song_name)
    
        
def run_server():
    # create a socket object
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_ip = "127.0.0.1"
    port = 8000

    server.bind((server_ip, port))
    print(f"Listening on {server_ip}:{port}")
    
    while True:
        server.listen(4)
        client_socket, client_address = server.accept()
        newClientThread=threading.Thread(target=run_client,args=(client_socket,client_address))
        newClientThread.start()

    
    
run_server()
