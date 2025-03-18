import socket
import subprocess
import sys
import platform

def start_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Сервер запущен и ожидает подключения на {host}:{port}...")

        conn, addr = server_socket.accept()
        with conn:
            print(f"Подключен клиент: {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                command = data.decode('utf-8')
                print(f"Получена команда: {command}")

                if command.strip().startswith("ping"):
                    if platform.system().lower() == "windows":
                        command = "ping -n 4 " + " ".join(command.split()[1:])
                    else:
                        command = "ping -c 4 " + " ".join(command.split()[1:])

                try:
                    output = subprocess.run(command, shell=True, capture_output=True, text=True)
                    result = output.stdout if output.stdout else output.stderr
                except Exception as e:
                    result = str(e)

                conn.sendall(result.encode('utf-8'))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8006
    host = "127.0.0.1"

    start_server(host, port)