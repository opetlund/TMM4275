from http.server import BaseHTTPRequestHandler, HTTPServer
import re
from pathlib import Path

HOST_NAME = '127.0.0.1'  # locathost - http://127.0.0.1
# Maybe set this to 1234 / So, complete address would be: http://127.0.0.1:1234
PORT_NUMBER = 1234
# Web servers example: http://www.ntnu.edu:80

pythonPath = "/Users/Hansro/Documents/I&IKT/Vår 2021/Auto 2/Python/"
dfaPath = "/templates/"

# File paths
dfa_template = Path("templates/chair_template.dfa")
userinterface_file = Path("templates/userinterface.html")
userinterface_error = Path("tmp/userinterface_error.html")
userinterface_tmp = Path("tmp/userinterface_tmp.html")
userinterface_order = Path("tmp/userinterface_order.html")
image_file = Path("theProduct.png")

variable_range = {
    "seat_depth": [35, 55],
    "chair_width": [30, 50],
    "back_height": [40, 60],
    "leg_side": [1, 10],
    "seat_height": [35, 55],
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


def update_defaults(template_filename, tmp_filename, params):
    # Sets the default values in html file
    file = open(template_filename)
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


def lock_and_order(filename):
    with open(filename, "r+") as file:
        data = file.read()
        find = 'input type="text"'
        replace = 'input readonly style="background-color:#80FF80;" type="text"'
        data = re.sub(find, replace, data)
        find = '<input type="submit" value="Check values">'
        replace = '<p>Chair is producible. </p><input type="submit" value="Create chair">'
        data = re.sub(find, replace, data)
        find = '</form>'
        replace = '</form><p></p><form action="/changeChair" method="post">\n<input type="submit" value="Re-enter values">\n</form>'
        data = re.sub(find, replace, data)
        find = 'orderChair'
        replace = 'submitChair'
        data = re.sub(find, replace, data)

        file.seek(0)
        file.write(data)
        file.truncate()


def set_error_message(min, max, variable, error_filename):
      # Sets the default values in html file
    file = open(error_filename)
    data = file.read()
    file.close()
    find = 'name="' + variable[0] + '"' + ' value=".*?">'
    # name="cdepth" value="123456"><br>
    replace = 'style="background-color:#FF0000;" name="' + str(variable[0]) + '"' + ' value="' + \
        variable[1] + '">' + \
        " Please insert a value between " + \
        str(round(min)) + " and " + str(round(max))
    data = re.sub(find, replace, data)
    file = open(error_filename, "wt")
    file.write(data)
    file.close()

# Handler of HTTP requests / responses


class MyHandler(BaseHTTPRequestHandler):

    # Function for displaying html file
    def write_HTML_file(self, filename):
        self.wfile.write(bytes(open(filename).read(), 'utf-8'))

    def do_GET(self):
        if self.path == '/' or self.path == "/orderChair":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.write_HTML_file(userinterface_file)

        elif(self.path == '/theproduct.png') != -1:
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            bReader = open(image_file, "rb")
            theImg = bReader.read()
            self.wfile.write(theImg)

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("Error. The file " +
                                   self.path + " does not exist.", 'utf-8'))

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
            update_defaults(userinterface_file,
                            userinterface_tmp,
                            params)
            update_defaults(userinterface_file,
                            userinterface_error,
                            params)
            update_defaults(userinterface_file,
                            userinterface_order,
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
                        userinterface_error)
                    illegal_value = True

            # html interface to show
            if illegal_value:
                self.write_HTML_file(userinterface_error)
                # self.wfile.write(
                #     bytes('<button onclick="myFunction()">Check values</button>', 'utf-8'))
                # self.wfile.write(bytes('<script>', 'utf-8'))
                # self.wfile.write(bytes('function myFunction() {', 'utf-8'))
                # self.wfile.write(bytes('var txt;', 'utf-8'))
                # self.wfile.write(
                #     bytes('var r = confirm("ERROR: The values is wrong!");', 'utf-8'))
                # self.wfile.write(bytes('}', 'utf-8'))
                # self.wfile.write(bytes('</script>', 'utf-8'))
                # self.wfile.write(bytes('</form>', 'utf-8'))
                # self.wfile.write(bytes('</body>', 'utf-8'))
                # self.wfile.write(bytes('</html>', 'utf-8'))
            else:
                lock_and_order(userinterface_order)
                self.write_HTML_file(userinterface_order)
                # self.wfile.write(
                #     bytes('<button onclick="myFunction()">Check values</button>', 'utf-8'))
                # self.wfile.write(bytes('<script>', 'utf-8'))
                # self.wfile.write(bytes('function myFunction() {', 'utf-8'))
                # self.wfile.write(bytes('var txt;', 'utf-8'))
                # self.wfile.write(
                #     bytes('var r = confirm("The values is OK!");', 'utf-8'))
                # self.wfile.write(bytes('}', 'utf-8'))
                # self.wfile.write(bytes('</script>', 'utf-8'))
                # self.wfile.write(
                #     bytes('<button>Create Chair</button>', 'utf-8'))
                # self.wfile.write(bytes('</form>', 'utf-8'))
                # self.wfile.write(bytes('<br>', 'utf-8'))
                # self.wfile.write(bytes('<br>', 'utf-8'))
                # self.wfile.write(bytes(
                #     '<img src="theProduct.png" alt="The product comes here" width="800" height="420">', 'utf-8'))
                # self.wfile.write(bytes('</body>', 'utf-8'))
                # self.wfile.write(bytes('</html>', 'utf-8'))

            # TODO: Give user response that chair is possible to create
            # TODO: And let user create chair
            # if not illegal_value:
            #     create_DFA(params, "user_chair.dfa",
            #                dfa_template)

        elif self.path.find("/submitChair") != -1:
            # Get the paramters
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            param_line = post_body.decode()
            params = parse_parameters(param_line)
            create_DFA(params, "user_chair.dfa",
                       dfa_template)
            self.write_HTML_file(userinterface_file)
            self.wfile.write(bytes('<script>', 'utf-8'))
            self.wfile.write(bytes('function myFunction() {', 'utf-8'))
            self.wfile.write(bytes('var txt;', 'utf-8'))
            self.wfile.write(
                bytes('var r = confirm("Chair created!");', 'utf-8'))
            self.wfile.write(bytes('}', 'utf-8'))
            self.wfile.write(bytes('myFunction()', 'utf-8'))
            self.wfile.write(bytes('</script>', 'utf-8'))
        elif self.path.find("/changeChair") != -1:
            self.write_HTML_file(userinterface_tmp)


if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
