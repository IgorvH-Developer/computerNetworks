import socketserver
import threading
import http.server
from urllib.parse import urlparse, unquote
import sys

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        parsed_path = urlparse(path)
        file_name = unquote(parsed_path.path.strip('/'))

        try:
            with open(file_name, 'rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, 'File not found')

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def process_request_thread(self, request, client_address):
        # Выводим адрес клиента при подключении
        print(f"Подключился клиент : {client_address}")
        super().process_request_thread(request, client_address)

def run_server(PORT):
    server = ThreadedTCPServer(("", PORT), RequestHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print("HTTP сервер запущен на порту:", PORT)

    while True:
        server.serve_forever()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8000

    run_server(port)