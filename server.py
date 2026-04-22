import socket
import wave
import json
import threading
import os
import ssl

MUSIC_FOLDER = "music"
BUFFER_SIZE = 2048

def init_details(client_socket, song_name):
    path = os.path.join(MUSIC_FOLDER, song_name)

    if not os.path.exists(path):
        error = {"status": "ERROR", "message": "File not found"}
        client_socket.send((json.dumps(error) + "\n").encode())
        return None

    with wave.open(path, 'rb') as wf:
        details = {
            "status": "OK",
            "smplwidth": wf.getsampwidth(),
            "channels": wf.getnchannels(),
            "framerate": wf.getframerate()
        }

        client_socket.send((json.dumps(details) + "\n").encode('utf-8'))
        return details

def read_data(client_socket,song_name):
    path = os.path.join(MUSIC_FOLDER, song_name)
    with wave.open(path, 'rb') as wf:
        while True:
            data=wf.readframes(1024)
            if data==b'':
                break
            client_socket.sendall(data)


def receive_json(client_socket):
    buffer = ""
    while True:
        buffer += client_socket.recv(1024).decode()
        if "\n" in buffer:
            msg, buffer = buffer.split("\n", 1)
            return json.loads(msg)

def run_client(client_socket, client_address):
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
    
    try:
        request = receive_json(client_socket)
        action = request.get("action")
        song_name = request.get("song")

        if action == "PLAY":
            init_details(client_socket, song_name)
            read_data(client_socket, song_name)
        else:
            error = {"status": "ERROR", "message": "Invalid action"}
            client_socket.send((json.dumps(error) + "\n").encode())

    except Exception as e:
        if "EOF occurred" in str(e):
            print(f"Client {client_address} closed connection")
        else:
            print(f"Error with client {client_address}: {e}")

    finally:
        print(f"Client disconnected: {client_address}")
        client_socket.close()

        
def run_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_ip = "0.0.0.0"
    port = 8000

    server.bind((server_ip, port))
    server.listen(5)  

    print(f"Listening on {server_ip}:{port}")
    
    while True:
        client_socket, client_address = server.accept()
        
        secure_socket = context.wrap_socket(client_socket, server_side=True)

        print(f"New client connected: {client_address}")

        newClientThread = threading.Thread(
            target=run_client,
            args=(secure_socket, client_address)
        )
        newClientThread.start()
    
    
run_server()
