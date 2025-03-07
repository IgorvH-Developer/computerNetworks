import socketserver
import threading
import http.server
from urllib.parse import urlparse, unquote
import sys

semaphore = None

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global semaphore

        semaphore.acquire()

        try:
            path = self.path
            parsed_path = urlparse(path)
            file_name = unquote(parsed_path.path.strip('/'))

            with open(file_name, 'rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, 'File not found')
        finally:
            semaphore.release()


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def process_request_thread(self, request, client_address):
        print(f"Подключился клиент : {client_address}")
        super().process_request_thread(request, client_address)


def run_server(port, concurrency_level):
    global semaphore

    semaphore = threading.Semaphore(concurrency_level)

    server = ThreadedTCPServer(("", port), RequestHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print("HTTP сервер запущен на порту:", port)

    while True:
        server.serve_forever()

if __name__ == "__main__":
    if len(sys.argv) > 2:
        port = int(sys.argv[1])
        concurrency_level = int(sys.argv[2])
    else:
        port = 8000
        concurrency_level = 10

    run_server(port, concurrency_level)