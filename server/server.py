import socket
import ssl
import threading

HOST = "0.0.0.0"
PORT = 5000

# Create normal socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

# Wrap socket with SSL
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="certificate.pem", keyfile="key.pem")

secure_server = context.wrap_socket(server, server_side=True)

print("Secure Quiz Server Started...")

def handle_client(client, addr):
    print(f"Client connected: {addr}")

    try:
        client.send("Welcome to Secure Quiz!\n".encode())

        while True:
            data = client.recv(1024).decode()

            if not data:
                break

            print(f"{addr}: {data}")

            if data.lower() == "exit":
                print(f"{addr} disconnected")
                break

            client.send("Received\n".encode())

    except:
        print(f"{addr} connection error")

    finally:
        client.close()


while True:
    client, addr = secure_server.accept()
    thread = threading.Thread(target=handle_client, args=(client, addr))
    thread.start()