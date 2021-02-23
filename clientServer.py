from http.server import BaseHTTPRequestHandler, HTTPServer
import re

HOST_NAME = '127.0.0.1'  # locathost - http://127.0.0.1
# Maybe set this to 1234 / So, complete address would be: http://127.0.0.1:1234
PORT_NUMBER = 1234
# Web servers example: http://www.ntnu.edu:80


variable_range = {
    "seat_depth": [0, 10],
    "chair_width": [0, 10],
    "back_height": [0, 10],
    "leg_side": [0, 10],
    "seat_height": [0, 10],
}
variable_to_DFA = {
    "seat_depth": "PARAM_SEAT_DEPTH",
    "chair_width": "PARAM_WIDTH",
    "back_height": "PARAM_BACK_HEIGHT",
    "leg_side": "PARAM_FRAME_THICKNESS",
    "seat_height": "PARAM_LEG_HEIGHT",
}


def create_DFA(params, dfa_filename, dfa_template):
    # Open dfa template
    file = open(dfa_template)
    dfa_data = file.read()
    file.close()

    # Insert parameter values
    for param_pair in params:
        find = "<" + variable_to_DFA[param_pair[0]] + ">"
        dfa_data = dfa_data.replace(find, param_pair[1])

    # Write to new dfa file
    file = open(dfa_filename, "wt")
    file.write(dfa_data)
    file.close()


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

# Handler of HTTP requests / responses


class MyHandler(BaseHTTPRequestHandler):

    # Function for displaying html file
    def write_HTML_file(self, filename):
        try:
            file = open(filename).read()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
        except:
            file = "Error. The file " + filename + " does not exist."
        self.wfile.write(bytes(file, 'utf-8'))

    def do_GET(self):
        if (self.path == '/') or (self.path.find("/orderChair") != -1):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
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

            # Update values in html files from param
            update_defaults("userinterface.html",
                            "userinterface_tmp.html",
                            "userinterface_error.html",
                            params)

            # Check for illegal parameter
            illegal_value = False

            for param_pair in params:
                param = param_pair[0]
                value = float(param_pair[1])
                min_value = variable_range[param][0]
                max_value = variable_range[param][1]
                if value < min_value or value > max_value:
                    set_error_message(
                        min_value,
                        max_value,
                        param_pair,
                        "userinterface_error.html")
                    illegal_value = True

            # html interface to show
            if illegal_value:
                self.write_HTML_file("userinterface_error.html")
            else:
                self.write_HTML_file("userinterface_tmp.html")

            if not illegal_value:
                create_DFA(params, "user_chair.dfa",
                           "my_chair_final_template.dfa")


if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
