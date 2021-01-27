from http.server import BaseHTTPRequestHandler, HTTPServer

HOST_NAME = '127.0.0.1'  # locathost - http://127.0.0.1
# Maybe set this to 1234 / So, complete address would be: http://127.0.0.1:1234
PORT_NUMBER = 1234
# Web servers example: http://www.ntnu.edu:80

# Handler of HTTP requests / responses


class MyHandler(BaseHTTPRequestHandler):

    # Function for displaying html file
    def write_HTML_file(self, path):
        self.path = path
        try:
            file = open(self.path[1:]).read()
            self.send_response(200)
        except:
            file = "file not found"
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file, 'utf-8'))

    def do_GET(self):
        if self.path == '/':
            self.write_HTML_file("7userinterface.html")


if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
