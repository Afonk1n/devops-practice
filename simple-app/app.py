from http.server import BaseHTTPRequestHandler, HTTPServer


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Hello from CI/CD demo app!\n")


def run():
    server_address = ("0.0.0.0", 8000)
    httpd = HTTPServer(server_address, SimpleHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    run()


