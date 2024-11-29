import socket
import threading
import os
from hashlib import sha256


IP = "172.20.2.137"  # this is my computers IP
PORT = 9999  # might need to change port too
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server"

os.makedirs(SERVER_PATH, exist_ok = True)

user = {"admin": sha256("password".encode()).hexdigest()}

client_storage = {}
file_metadata = {}


def authentication(client_socket):  # authenticate using sha256 encryption
    client_socket.send("Log in:".encode(FORMAT))
    qualification = client_socket.recv(SIZE).decode(FORMAT).split(":")
    username, password = qualification[0], qualification[1]
    hashed_pass = sha256(password.encode()).hexdigest()
    if username in user and user[username] == hashed_pass:
        client_socket.send("OK@Login success.".encode(FORMAT))
        return True
    client_socket.send("ERROR@Invalid login.".encode(FORMAT))
    return False


def file_name(filename, file_type):
    prefix = {"text": "TS", "audio": "AS", "video": "VS"}.get(file_type, "FS")
    count = len([name for name in file_metadata if file_metadata[name]["type"] == file_type])
    return f"{prefix}{count + 1:03}"


def handle_client(client_socket, address):
    print(f"New Client Connection: {address} connected.")
    if not authentication(client_socket):
        print(f"[DISCONNECT] {address} failed authentication.")
        client_socket.close()
        return

    while True:
        try:
            data = client_socket.recv(SIZE).decode(FORMAT)
            if not data:
                break
            cmd = data.split("@")[0].upper()

            if cmd == "LOGOUT":
                print(f"[DISCONNECTED] {address} logged out. ")
                client_socket.send("OK@Goodbye. ".encode(FORMAT))
                break
            elif cmd == "DIR":
                files = os.listdir(SERVER_PATH)
                response = "\n".join(files) if files else "No files available. "
                client_socket.send(f"OK@{response}".encode(FORMAT))

            elif cmd == "UPLOAD":
                filename = data.split("@")[1]
                file_type = "text" if filename.endswith(".txt") else "video"
                unique_name = file_name(filename, file_type)
                file_data = client_socket.recv(SIZE)
                with open(os.path.join(SERVER_PATH, unique_name), "wb") as f:
                    f.write(file_data)
                file_metadata[unique_name] = {"type": file_type, "size": len(file_data)}
                client_socket.send(f"OK@{unique_name} upload success.".encode(FORMAT))

            elif cmd == "DOWNLOAD":
                unique_name = data.split("@")[1]
                filepath = os.path.join(SERVER_PATH, unique_name)
                if os.path.exists(filepath):
                    with open(filepath, "rb") as f:
                        client_socket.sendall(f.read())
                else:
                    client_socket.send("ERROR@File not found. ".encode(FORMAT))

            else:
                client_socket.send("ERROR@Invalid command. ".encode(FORMAT))

        except Exception as e:
            print(f"[ERROR] {address} : {e}")
            break

    client_socket.close()


def main():
    print("Starting server")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"server is listening on {IP}: {PORT}")

    while True:
        file, address = server.accept()
        thread = threading.Thread(target = handle_client, args = (file, address))
        thread.start()


if __name__ == "__main__":
    main()


