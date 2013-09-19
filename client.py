#!/usr/bin/python

from optparse import OptionParser 
from collections import deque
import socket
import ssl

# A HTTPResponse is a:
# (HTTPHeader, HTML)

# A HTTPHeader is a map
# {"HTTP fieldname": ["<field value>"]
#  "HTTP fieldname": ["<value1", "value2"]
#   ...
# }

# A HTML is a String


to_visit = deque()
visited = set()

# .append() and .popleft() [to_visit]

FAKEBOOK_HOST = "cs5700.ccs.neu.edu"
FAKEBOOK_HOME = "/accounts/login/?next=/fakebook/"

cookie_store = {
    'csrftoken': None,
    'sessionid': None
}

# HTTPResponse -> 
# Given an HTTPResponse, store the cookie values
def store_cookies(response):
    cookies = response["Set-cookie:"]
    for i in cookies:
        store_cookie(cookies[i])

# Store a Fakebook cookie
# String -> 
def store_cookie(cookie):
    global cookie_store
    if 'name=csrftoken' in cookie:
        cookie_store["csrftoken"] = cookie
    elif 'name=sessionid' in cookie:
        cookie_store["sessionid"] = cookie

# Retrieve the cookies
# -> String
def retrieve_cookies():
    global cookie_store
    cookie_str = ""
    for i in cookie_store:
        if cookie_store[i]:
            cookie_str += cookie_store[i]
            cookie_str += "; "
    return cookie_str

# Parse the commandline input into a map of 
# name to values
def parse_input():
    usage = "usage: %prog username password"
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("incorrect number of arguments")
    else:
        options.username = args[0]
        options.password = args[1]
    return options

# Open a socket to the server
def open_socket(server, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect((server, port))
    return s

# Close the socket
def close_socket(socket):
    socket.close()

# Parse the socket data
def split_http(data):
    return data.split('\r\n\r\n\n', 1)

# Receive data from the socket
def recv_data(socket):
    return socket.recv(4096)

# Send data on the socket
def send_data(socket, data):
    return socket.send(data)

# Turn a plain text header into a dictionary
def parse_header(data):
    header = {}
    for line in data.split("\r\n"):
        line = line.split(': ', 1)
        if len(line) == 2:
            if not line[0] in header:
                header[line[0]] = list()
            header[line[0]].append(line[1])
        else:
            header['response_code'] = line[0].split(' ')[1]
    return header

# Create a GET request for the specified url path
def http_get(socket, host, path, cookies=""):
    header =  "GET %s HTTP/1.1\n" % path
    header += "Host: %s\n" % host
    if cookies != "":
        header += "Cookies: %s\n" % cookies 
    header += "\n"

    sent_bytes = send_data(socket, header)

    response = split_http(recv_data(socket))
    header = parse_header(response[0])
    body = response[1]

    return (header, body)

# Convert map into form encoded key=value string
def form_encode(form_data):
    ret = ""
    for key,value in form_data.items():
        if len(ret):
            ret += "&"
        ret += "%s=%s"

# Send a POST for the specified url path with the specified form data
def http_post(socket, host, path, form_data, cookies=""):
    encoded = form_encode(form_data)
    header = "POST %s HTTP/1.1\n" % path
    header += "Content-Type: application/x-www-form-urlencoded\n"
    header += "Content-Length: %d\n" % len(encoded)
    header += "\n"
    header += encoded

# Wrap the socket to allow for easy sending
# Socket -> [String -> ]
def wrap_get(socket):
    return lambda path:
        return http_get(socket, FAKEBOOK_HOST, path, retrieve_cookies()))

# Wrap the socket to allow for easy sending
# Socket -> [String -> ]
def wrap_post(socket):
    return lambda path,form_data:
        return http_post(socket, FACEBOOK_HOST, path, form_data, retrieve_cookies())

def do_login():
    login_page = http_get(socket, FAKEBOOK_HOST, FAKEBOOK_HOME)
    print login_page


# Entry point to the program
def main():
    args = parse_input()

    # Create a connection to the server
    socket = open_socket(FAKEBOOK_HOST, 80)
    get = wrap_get(socket)    

    if not do_login(socket):
       print "Could not login" 
       exit(0)
    
    while len(to_visit) > 0:
        path = to_visit.popleft()
        (header, body) = get(path)
        status = header["resp_code"]
        if status == "200":
            parse_body(body)
        elif status == "301":
            handle_redirect(header, body)
        elif status == "500":
            to_visit.append(path)

    # not necessary, but nice to close the socket
    close_socket(socket)















# These 2 lines allow us to import this file into another file 
# and test individual components without running it
if __name__ == "__main__":
    main()
