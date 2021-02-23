from http.server import BaseHTTPRequestHandler, HTTPServer
import re

HOST_NAME = '127.0.0.1'  # locathost - http://127.0.0.1
# Maybe set this to 1234 / So, complete address would be: http://127.0.0.1:1234
PORT_NUMBER = 1234
# Web servers example: http://www.ntnu.edu:80


variable_range = [
    # [name, min, max]
    ['clength', 0, 1000],
    ['cheight', 0, 2000],
    ['cwidth',  0, 500],
    ['cdepth',  0, 500]
]
variable_range2 = {
    "seat_depth": [0, 10],
    "chair_width": [0, 10],
    "back_height": [0, 10],
    "leg_side": [0, 10],
    "seat_height": [0, 10],
}

# Handler of HTTP requests / responses


def parse_parameters(string):
    # Returns list of elements of ["param", "value"]
    params = string.split("&")
    for i, val in enumerate(params):
        params[i] = val.split("=")
    return params


def update_defaults(filename, tmp_filename, error_filename, params):
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
    file = open(error_filename, "wt")
    file.write(data)
    file.close()


def set_error_message(min, max, variable, error_filename):
      # Sets the default values in html file
    file = open(error_filename)
    data = file.read()
    file.close()
    find = 'name="' + variable[0] + '"' + ' value=".*?">'
    # name="cdepth" value="123456"><br>
    replace = 'name="' + str(variable[0]) + '"' + ' value="' + \
        variable[1] + '">' + \
        " Error. Parameter value is out of range. Please insert a value between " + \
        str(round(min)) + " and " + str(round(max))
    data = re.sub(find, replace, data)
    file = open(error_filename, "wt")
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
        if (self.path == '/') or (self.path.find("/orderChair") != -1) or (self.path.find("/userinterface.html") != -1):
            self.path = "/orderChair/userinterface.html"
            self.write_HTML_file("userinterface.html")

    def do_POST(self):

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        if self.path.find("/orderChair") != -1:
            # Get the paramters
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            param_line = post_body.decode()
            params = parse_parameters(param_line)
            print(params)

            update_defaults("userinterface.html",
                            "userinterface_tmp.html",
                            "userinterface_error.html",
                            params)

            # for i in range(len(params)):
            #params[i][1] = float(params[i][1])

            length = float(params[0][1])
            height = float(params[1][1])
            width = float(params[2][1])
            depth = float(params[3][1])

            illegal_value = False

            for i, param in enumerate(params):
                value = float(param[1])
                min_value = variable_range[i][1]
                max_value = variable_range[i][2]
                if value < min_value or value > max_value:
                    set_error_message(
                        min_value,
                        max_value,
                        param,
                        "userinterface_error.html")
                    illegal_value = True

            # html interface to show
            if illegal_value:
                self.write_HTML_file("userinterface_error.html")
            else:
                self.write_HTML_file("userinterface_tmp.html")


if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
