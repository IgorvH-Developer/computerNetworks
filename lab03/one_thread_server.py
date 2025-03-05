import http.server
import socketserver
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


def run_server(port):
    with socketserver.TCPServer(("", port), RequestHandler) as httpd:
        print(f"Serving at port {port}")
        httpd.serve_forever()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8000

    run_server(port)