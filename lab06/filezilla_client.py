import socket
import os

class FTPClient:
    def __init__(self, host, port=21):
        self.host = host
        self.port = port
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_socket = None
        self.data_port = None

    def connect(self):
        self.control_socket.connect((self.host, self.port))
        response = self.get_response()
        print(response)
        return response.startswith("220")

    def login(self, username, password):
        self.send_command(f"USER {username}")
        response = self.get_response()
        print(response)
        if not response.startswith("331"):
            return False

        self.send_command(f"PASS {password}")
        response = self.get_response()
        print(response)
        return response.startswith("230")

    def list_files(self):
        self.setup_data_connection("PASV")
        self.send_command("LIST")
        response = self.get_response()
        print(response)

        data = self.receive_data()
        self.data_socket.close()
        self.get_response()
        print("Список файлов:")
        print(data.decode("utf-8"))

    def upload_file(self, local_path, remote_path):
        if not os.path.exists(local_path):
            print(f"Ошибка: файл {local_path} не найден!")
            return False

        self.setup_data_connection("PASV")
        self.send_command(f"STOR {remote_path}")
        response = self.get_response()
        print(response)

        with open(local_path, "rb") as file:
            data = file.read()
            self.data_socket.sendall(data)

        self.data_socket.close()
        response = self.get_response()
        print(response)
        return response.startswith("226")

    def download_file(self, remote_path, local_path):
        self.setup_data_connection("PASV")
        self.send_command(f"RETR {remote_path}")
        response = self.get_response()
        print(response)

        data = self.receive_data()
        self.data_socket.close()
        self.get_response()

        with open(local_path, "wb") as file:
            file.write(data)
        print(f"Файл сохранён как {local_path}")

    def setup_data_connection(self, mode="PASV"):
        if mode == "PASV":
            self.send_command("PASV")
            response = self.get_response()
            print(response)

            if not response.startswith("227"):
                raise Exception("Ошибка PASV-режима!")

            parts = response.split("(")[1].split(")")[0].split(",")
            ip = ".".join(parts[:4])
            port = int(parts[4]) * 256 + int(parts[5])

            self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.data_socket.connect((ip, port))

    def send_command(self, command):
        self.control_socket.sendall(f"{command}\r\n".encode("utf-8"))

    def get_response(self):
        response = b""
        while True:
            part = self.control_socket.recv(1024)
            response += part
            if len(part) < 1024 or part[-2:] == b"\r\n":
                break
        return response.decode("utf-8").strip()

    def receive_data(self):
        """Получение данных через data-соединение."""
        data = b""
        while True:
            part = self.data_socket.recv(4096)
            if not part:
                break
            data += part
        return data

    def quit(self):
        """Закрытие соединения."""
        self.send_command("QUIT")
        response = self.get_response()
        print(response)
        self.control_socket.close()

if __name__ == "__main__":
    client = FTPClient("ftp.dlptest.com", 21)
    if client.connect() and client.login("dlpuser", "rNrKYTX9g7z3RgJRmxWuGHbeu"):
        client.list_files()
        client.upload_file("example.txt", "uploaded.txt")  # Загрузить файл
        client.download_file("uploaded.txt", "downloaded.txt")  # Скачать файл
        client.quit()