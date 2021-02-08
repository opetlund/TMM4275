from http.server import BaseHTTPRequestHandler, HTTPServer
import re

HOST_NAME = '127.0.0.1'  # locathost - http://127.0.0.1
# Maybe set this to 1234 / So, complete address would be: http://127.0.0.1:1234
PORT_NUMBER = 1234
# Web servers example: http://www.ntnu.edu:80

length_min = 100
height_min = 100
width_min = 100
depth_min = 100

length_max = 1000
height_max = 1000
width_max = 1000
depth_max = 1000

# Handler of HTTP requests / responses


def parse_parameters(string):
    # Returns list of elements of ["param", "value"]
    params = string.split("&")
    for i, val in enumerate(params):
        params[i] = val.split("=")
    return params


def update_defaults(filename, tmp_filename, params):
    # Sets the default values in html file
    file = open(filename)
    data = file.read()
    file.close()
    for param in params:
        find = 'name="' + param[0] + '"' + ' value=".*?"'
        # name="cdepth" value="123456"><br>
        replace = 'name="' + param[0] + '"' + ' value="' + param[1] + '"'
        data = re.sub(find, replace, data)
    file = open(tmp_filename, "wt")
    file.write(data)
    file.close()


def set_error_message(min, max, variable, filename, tmp_filename):
      # Sets the default values in html file
    file = open(filename)
    data = file.read()
    file.close()
    find = 'name="' + variable[0] + '"' + ' value=".*?">'
    # name="cdepth" value="123456"><br>
    replace = 'name="' + str(variable[0]) + '"' + ' value="' + \
        variable[1] + '">' + "Error. Value is out of bounds."
    data = re.sub(find, replace, data)
    file = open(tmp_filename, "wt")
    file.write(data)
    file.close()


class MyHandler(BaseHTTPRequestHandler):

    # Function for displaying html file
    def write_HTML_file(self, filename):
        try:
            file = open(filename).read()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
        except:
            file = "Error. File not found."
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file, 'utf-8'))

    def do_GET(self):
        if self.path == '/' or self.path == "/orderChair":
            self.write_HTML_file("userinterface.html")

    def do_POST(self):

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # Check what is the path
        path = self.path
        if path.find("/orderChair") != -1:
            # Get the paramters
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            param_line = post_body.decode()
            params = parse_parameters(param_line)

            # for i in range(len(params)):
            #params[i][1] = float(params[i][1])

            length = float(params[0][1])
            height = params[1][1]
            width = params[2][1]
            depth = params[3][1]

            if length_min > length or length_max < length:
                set_error_message(
                    length_min, length_max, params[0], "userinterface.html", "userinterfacetmp2.html")
                self.write_HTML_file("userinterfacetmp2.html")
            # # html interface to show
            # update_defaults("userinterface.html",
            #                 "userinterface_tmp.html",
            #                 params)
            # self.write_HTML_file("userinterface_tmp.html")


if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
