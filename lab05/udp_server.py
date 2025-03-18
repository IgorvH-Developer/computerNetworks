import socket
import time
from datetime import datetime
import sys

def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    print(f"Сервер запущен и рассылает время на порт {port}...")

    while True:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Текущее время: {current_time}"

        server_socket.sendto(message.encode('utf-8'), ('<broadcast>', port))
        print(f"Отправлено: {message}")

        time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8006

    start_server(port)