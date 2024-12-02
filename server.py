import socket
import threading
import os
from hashlib import sha256
import shutil

IP = "10.200.237.239"  # this is my computers IP
PORT = 9999  # might need to change port too
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server"

os.makedirs(SERVER_PATH, exist_ok=True)

user = {"admin": sha256("password".encode()).hexdigest()}

client_storage = {}
file_metadata = {}


def authentication(client_socket):  # authenticate using sha256 encryption
    qualification = client_socket.recv(SIZE).decode(FORMAT).split(":")
    username, password = qualification[0], qualification[1]
    hashed_pass = password
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
                filepath = os.path.join(SERVER_PATH, filename)

                # Check if file exists
                if os.path.exists(filepath):
                    client_socket.send("ERROR@File already exists.".encode(FORMAT))
                else:
                    # Save the file
                    incoming_data = client_socket.recv(SIZE)
                    with open(filepath, "wb") as f:
                        f.write(incoming_data)
                    client_socket.send(f"OK@{filename} upload success.".encode(FORMAT))

            elif cmd == "DOWNLOAD":
                unique_name = data.split("@")[1]
                filepath = os.path.join(SERVER_PATH, unique_name)
                if os.path.exists(filepath):
                    with open(filepath, "rb") as f:
                        client_socket.sendall(f.read())
                else:
                    client_socket.send("ERROR@File not found. ".encode(FORMAT))

            elif cmd == "DELETE_FILE":
                filename = data.split("@")[1]
                filepath = os.path.join(SERVER_PATH, filename)
                if os.path.exists(filepath) and os.path.isfile(filepath):
                    os.remove(filepath)
                    client_socket.send(f"OKFile@{filename} delete success. ".encode(FORMAT))
                else:
                    client_socket.send("ERROR@File not found or invalid. ".encode(FORMAT))

            elif cmd == "CREATE_FOLDER":
                folder_name = data.split("@")[1]
                folder_path = os.path.join(SERVER_PATH, folder_name)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    client_socket.send(f"OK@Folder '{folder_name}' created successfully. ".encode(FORMAT))
                else:
                    client_socket.send("ERROR@Folder already exist ".encode(FORMAT))

            elif cmd == "DELETE_FOLDER":
                folder_name = data.split("@")[1]
                folder_path = os.path.join(SERVER_PATH, folder_name)
                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    shutil.rmtree(folder_path)
                    client_socket.send(f"OK@Folder '{folder_name}' deleted successfully.".encode(FORMAT))
                else:
                    client_socket.send("ERROR@Folder not found or invalid. ".encode(FORMAT))

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
        thread = threading.Thread(target=handle_client, args = (file, address))
        thread.start()


if __name__ == "__main__":
    main()


