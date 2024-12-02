import socket
import os
from hashlib import sha256

SERVER_HOST = "10.200.237.239"  # just made it the same as what you have for server.py
SERVER_PORT = 9999  # same as what you have
ADDR = (SERVER_HOST, SERVER_PORT)
SIZE = 1024
FORMAT = "utf-8"
CLIENT_PATH = "client"  # supposed to be local directory to where you want to save the download files from the server

os.makedirs(CLIENT_PATH, exist_ok=True)


def connect_to_server():
    # this connects to the server and returns the socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"[CONNECTED] Connected to server at {SERVER_HOST}:{SERVER_PORT}")
        return client_socket  # returns connected client_socket object so client can use it
    except Exception as e:
        print(f"[ERROR] Could not connect to server: {e}")
        return None


def authenticate(client_socket):
    username = input("Enter username: ")
    password = input("Enter password: ")
    hashed_password = sha256(password.encode()).hexdigest()

    client_socket.sendall(f"{username}:{hashed_password}".encode(FORMAT))
    response = client_socket.recv(SIZE).decode(FORMAT)
    if response.startswith("OK"):
        print("[AUTHENTICATED] Successfully logged in.")
        return True
    else:
        print("[AUTH FAILED] Invalid credentials.")
        return False


def upload_file(client_socket):
    filepath = input("Enter the path of the file to upload: ").strip()

    if not os.path.exists(filepath):
        print("[ERROR] File not found.")
        return

    filename = os.path.basename(filepath)
    client_socket.sendall(f"UPLOAD@{filename}".encode(FORMAT))

    with open(filepath, "rb") as file:
        data = file.read()
        client_socket.sendall(data)
    # stops duplicates
    response = client_socket.recv(SIZE).decode(FORMAT)
    if response.startswith("ERROR"):
        print(response.split("@")[1])
    else:
        print(response.split("@")[1])


def download_file(client_socket):
    filename = input("Enter the filename to download: ").strip()
    client_socket.sendall(f"DOWNLOAD@{filename}".encode(FORMAT))

    response = client_socket.recv(SIZE).decode(FORMAT)
    if response.startswith("ERROR"):
        print(response.split("@")[1])
    else:
        with open(os.path.join(CLIENT_PATH, filename), "wb") as file: file.write(response.encode(FORMAT))
        print(F"[SUCCESS] File {filename} downloaded successfully.")


def view_directory(client_socket):
    client_socket.sendall("DIR".encode(FORMAT))
    response = client_socket.recv(SIZE).decode(FORMAT)
    print(f"Server Files:\n{response.split('@')[1]}")


def delete_file(client_socket):
    filename = input("Enter the filename to delete: ").strip()
    client_socket.sendall(f"DELETE_FILE@{filename}".encode(FORMAT))
    response = client_socket.recv(SIZE).decode(FORMAT)
    print(response.split("@")[1])  # displays server's response


def create_file(client_socket):
    filename = input("Enter the filename to create: ").strip()
    client_socket.sendall(f"CREATE@{filename}".encode(FORMAT))
    response = client_socket.recv(SIZE).decode(FORMAT)
    print(response.split("@")[1])


def create_subfolder(client_socket):
    folder_name = input("Enter the name of the folder to create: ")
    client_socket.sendall(f"CREATE_FOLDER@{folder_name}".encode(FORMAT))
    response = client_socket.recv(SIZE).decode(FORMAT)
    print(response.split("@")[1])


def delete_subfolder(client_socket):
    folder_name = input("Enter the name of the folder to delete: ")
    client_socket.sendall(f"DELETE_FOLDER@{folder_name}".encode(FORMAT))
    response = client_socket.recv(SIZE).decode(FORMAT)
    print(response.split("@")[1])


def logout(client_socket):
    client_socket.sendall("LOGOUT".encode(FORMAT))
    response = client_socket.recv(SIZE).decode(FORMAT)
    print(response.split("@")[1])


def main():
    client_socket = connect_to_server()
    if not client_socket:
        return

    if not authenticate(client_socket):
        client_socket.close()
        return

    while True:
        print("\nMenu:")
        print("1. Upload file")
        print("2. Download file")
        print("3. View server directory")
        print("4. Delete file")
        print("5. Create folder")
        print("6. Delete folder")
        print("7. Log out")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            upload_file(client_socket)
        elif choice == "2":
            download_file(client_socket)
        elif choice == "3":
            view_directory(client_socket)
        elif choice == "4":
            delete_file(client_socket)
        elif choice == "5":
            create_subfolder(client_socket)
        elif choice == "6":
            delete_subfolder(client_socket)
        elif choice == "7":
            logout(client_socket)
            client_socket.close()
            break
        else:
            print("[ERROR] Invalid input. Please try again.")


if __name__ == "__main__":
    main()