import socket
import ssl

SERVER_IP = "192.168.29.45"
PORT = 5000

# Create socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Create SSL context
context = ssl.create_default_context()

# Disable certificate verification for testing (important)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

# Wrap socket
secure_client = context.wrap_socket(client, server_hostname=SERVER_IP)

secure_client.connect((SERVER_IP, PORT))

print("Connected securely to server")

while True:
    msg = input("Enter message (type exit to quit): ")

    secure_client.send(msg.encode())

    if msg.lower() == "exit":
        break

    data = secure_client.recv(1024).decode()
    print("Server:", data)

secure_client.close()