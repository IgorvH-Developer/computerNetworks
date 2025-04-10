import socket
import os
from stop_wait_protocol import StopWaitProtocol


def send_file(filename: str, server_addr: tuple):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rdt = StopWaitProtocol(sock)

    with open(filename, 'rb') as f:
        file_data = f.read()

    # Отправка имени файла и размера
    file_info = f"{os.path.basename(filename)}|{len(file_data)}".encode()
    rdt.send_packet(file_info, server_addr)

    print("отправил название и размер")

    # Отправка файла по частям (по 1020 байта)
    packet_size = 1020
    for i in range(0, len(file_data), packet_size):
        chunk = file_data[i:i + packet_size]
        rdt.send_packet(chunk, server_addr)

    print(f"File {filename} sent successfully")


def receive_file(save_path: str, server_addr: tuple):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rdt = StopWaitProtocol(sock)

    # Запрос файла у сервера
    rdt.send_packet(b'REQUEST_FILE', server_addr)

    # Получение информации о файле
    file_info, _ = rdt.recv_packet()
    filename, file_size = file_info.decode().split('|')
    file_size = int(file_size)

    # Получение файла
    received_data = bytearray()
    while len(received_data) < file_size:
        chunk, _ = rdt.recv_packet()
        received_data.extend(chunk)

    # Сохранение файла
    with open(os.path.join(save_path, filename), 'wb') as f:
        f.write(received_data)

    print(f"File {filename} received successfully")


if __name__ == "__main__":
    server_address = ('localhost', 12345)

    # Пример использования:
    # Отправка файла на сервер
    # send_file('alice.txt', server_address)

    # Получение файла с сервера
    receive_file('./downloads', server_address)