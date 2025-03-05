import socket
import sys

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Неверный формат команды.")
        sys.exit(1)

    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    filename = sys.argv[3]

    request = f'GET /{filename} HTTP/1.1\r\nHost: {server_host}\r\nConnection: close\r\n\r\n'

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((server_host, server_port))
            sock.sendall(request.encode())

            response = b''
            while True:
                data = sock.recv(1024)
                if not data:
                    break
                response += data

        print(response.decode('utf-8'))
    except Exception as e:
        print(f"Произошла ошибка: {e}")