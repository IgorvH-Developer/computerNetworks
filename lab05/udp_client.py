import socket
import sys

def start_client(port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Привязываем сокет к любому адресу и указанному порту
    client_socket.bind(('', port))

    print(f"Клиент запущен и ожидает сообщений на порту {port}...")

    while True:
        data, addr = client_socket.recvfrom(1024)
        print(f"Получено сообщение от {addr}: {data.decode('utf-8')}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8006

    start_client(port)