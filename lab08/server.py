import socket
import os
from stop_wait_protocol import StopWaitProtocol


def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 12345))
    print("Server started on port 12345")

    rdt = StopWaitProtocol(sock)

    while True:
        # Получение первого пакета (информация о файле или запрос)
        first_packet, addr = rdt.recv_packet()

        if first_packet == b'REQUEST_FILE':
            # Клиент запрашивает файл
            send_file('server_file.txt', addr, rdt)
        else:
            # Клиент отправляет файл
            receive_file(first_packet, addr, rdt)


def receive_file(file_info: bytes, addr: tuple, rdt: StopWaitProtocol):
    filename, file_size = file_info.decode().split('|')
    file_size = int(file_size)

    received_data = bytearray()
    while len(received_data) < file_size:
        chunk, _ = rdt.recv_packet()
        received_data.extend(chunk)

    # Сохранение файла
    with open(os.path.join('uploads', filename), 'wb') as f:
        f.write(received_data)

    print(f"File {filename} received from {addr}")


def send_file(filename: str, addr: tuple, rdt: StopWaitProtocol):
    try:
        with open(filename, 'rb') as f:
            file_data = f.read()

        # Отправка информации о файле
        file_info = f"{os.path.basename(filename)}|{len(file_data)}".encode()
        rdt.send_packet(file_info, addr)

        # Отправка файла по частям
        packet_size = 1024
        for i in range(0, len(file_data), packet_size):
            chunk = file_data[i:i + packet_size]
            rdt.send_packet(chunk, addr)

        print(f"File {filename} sent to {addr}")
    except FileNotFoundError:
        error_msg = "FILE_NOT_FOUND".encode()
        rdt.send_packet(error_msg, addr)


if __name__ == "__main__":
    # Создание директорий для загрузок
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('downloads', exist_ok=True)

    # Создание тестового файла на сервере
    with open('server_file.txt', 'w') as f:
        f.write("This is a test file from the server.")

    start_server()