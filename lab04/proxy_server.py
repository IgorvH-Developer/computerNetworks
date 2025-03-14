import os
import time
import hashlib
import socket
import threading
from urllib.parse import urlparse, parse_qs
import sys

def parse_headers(headers):
    return dict(h.split(": ", 1) for h in headers.split("\r\n") if ": " in h)

def get_response(server_socket):
    response = b''
    chunk_size = 8192
    content_length = None
    remaining_data = 0
    while content_length is None or remaining_data > 0:
        if content_length is not None:
            data = server_socket.recv(min(remaining_data, chunk_size))
        else:
            data = server_socket.recv(chunk_size)
        if not data:
            content_length = None
            remaining_data = 0
            break
        response += data

        if content_length is None:
            for line in response.split(b'\r\n'):
                if b'Content-Length:' in line:
                    content_length = int(line.split(b':', 1)[1].strip())
                    remaining_data = content_length - len(response)
        else:
            remaining_data -= len(data)

    return response

def transformRequest(request, host, method, url, protocol):
    headers = request.decode().split("\r\n\r\n")[0]
    header_dict = parse_headers(headers)

    header_dict['Host'] = host
    header_dict['User-Agent'] = 'MyProxyServer'

    new_request = f"{method} {url} {protocol}\r\n" if ("Referer" in header_dict) else f"{method} / {protocol}\r\n"
    if "Referer" in header_dict:
        refererHost = header_dict["Referer"].split('/')
        header_dict["Referer"] = '/'.join(refererHost[:2]) + '/' + '/'.join(refererHost[3:])
        header_dict['Host'] = '/'.join(refererHost[3:])
    for key, value in header_dict.items():
        new_request += f"{key}: {value}\r\n"
    new_request += "\r\n"
    return new_request, header_dict['Host']

def proxy_server(client_socket, addr):
    request = client_socket.recv(4096)

    # Парсим запрос
    first_line = request.decode().split('\n')[0]
    method, path, protocol = first_line.split()
    parsed_url = urlparse(path)

    if method == 'GET':
        host = parsed_url.netloc or parsed_url.path.strip('/')
        url = parsed_url.geturl()
    elif method == 'POST':
        params = parse_qs(parsed_url.query)
        host = params['host'][0]
        url = host

    cache_dir = "cache/"
    cached_file_path = os.path.join(cache_dir, hashlib.md5(url.encode()).hexdigest())

    if os.path.exists(cached_file_path):
        with open(cached_file_path, 'rb') as cached_file:
            response = cached_file.read()  # Читаем ответ из кеша
        print(f"Serving from cache: {cached_file_path}")
    else:
        new_request, new_host = transformRequest(request, host, "GET", url, protocol)

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((new_host, 80))

        server_socket.sendall(new_request.encode())

        response = get_response(server_socket)

        resp_first_item = response.split(b"\r\n")[0]
        print(f'Requested {new_host}, Response code: {resp_first_item}')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        with open(cached_file_path, 'wb') as cached_file:
            cached_file.write(response)
    client_socket.sendall(response)

    client_socket.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8006

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("", port))
    server_socket.listen(10)

    print(f'Server started on port {port}')

    try:
        while True:
            client_socket, addr = server_socket.accept()

            thread = threading.Thread(target=proxy_server, args=(client_socket, addr))
            thread.start()
    except KeyboardInterrupt:
        server_socket.close()