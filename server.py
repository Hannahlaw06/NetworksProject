import socket
import threading

IP = "localhost"  # need to change to other computer IP
PORT = 9999  # might need to change port too
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server"


def handle_client(file, address):
    print(f"New Client Connection: {address} connected.")
    file.send("OK@Welcome to the server".encode(FORMAT))

    while True:
        data = file.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]

        send_data = "OK@"

        if cmd == "LOGOUT":
            break
        elif cmd == "TASK":
            send_data += "LOGOUT from server.\n"
        file.send(send_data.encode(FORMAT))

        print(f"{address} disconnected")
        file.close()


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


