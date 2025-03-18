import socket
import sys

def send_command(command, host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        client_socket.sendall(command.encode('utf-8'))
        data = client_socket.recv(1024)
        print(f"Результат выполнения команды:\n{data.decode('utf-8')}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        server_port = int(sys.argv[1])
    else:
        server_port = 8006
    server_host = "127.0.0.1"

    command = input("Введите команду для выполнения на сервере: ")
    send_command(command, server_host, server_port)