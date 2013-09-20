#!/usr/bin/python

from optparse import OptionParser 
from collections import deque
import socket
import urllib

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
FAKEBOOK_HOME = r"/accounts/login/?next=%2Ffakebook%2F"
FAKEBOOK_LOGIN = "/accounts/login/"

cookie_store = {
    'csrftoken': None,
    'sessionid': None
}

# -> String
# Parse the csrftoken out of the cookie
def parse_token(cookie):
    key_value = cookie.split(";")[0]
    values = key_value.split("=")
    return (values[0], values[1])

# HTTPHeader -> 
# Given an HTTPHeader, store the cookie values
def store_cookies(header):
    global cookie_store
    cookies = header["Set-Cookie"]
    for cookie in cookies:
        (name, value) = parse_token(cookie)
        cookie_store[name] = value

# Retrieve the cookies
# -> String
def retrieve_cookies():
    global cookie_store
    cookie_str = ""
    for i in cookie_store:
        if cookie_store[i]:
            cookie_str += i
            cookie_str += "="
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

# Create a connection to the server
# -> Socket
def create_connection():
    return open_socket(FAKEBOOK_HOST, 80)

# Close the socket
def close_socket(socket):
    socket.close()

# Parse the socket data
def split_http(data):
    return data.split('\r\n\r\n', 1)

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

# String String Dict String -> HTTPResponse
# Send a POST for the specified url path with the specified form data
def http_post(host, path, form_data, cookies):
    socket = create_connection()

    encoded = form_encode(form_data)
    header = "POST %s HTTP/1.1\n" % path
    header += "Host: %s\n" % host
    header += "Content-Type: application/x-www-form-urlencoded\n"
    header += "Content-Length: %d\n" % len(encoded)
    header += "Cookie: %s\n" % cookies
    header += "\n"
    header += encoded

    sent_bytes = send_data(socket, header)

    response = split_http(recv_data(socket))
    header = parse_header(response[0])
    body = response[1]

    close_connection(socket)

    return (header, body)

# Create a GET request for the specified url path
def http_get(host, path, cookies):
    socket = create_connection()
    header =  "GET %s HTTP/1.1\n" % path
    header += "Host: %s\n" % host
    if cookies != None:
        header += "Cookie: %s\n" % cookies 
    header += "\n"

    sent_bytes = send_data(socket, header)

    response = split_http(recv_data(socket))
    header = parse_header(response[0])
    body = response[1]

    close_connection(socket)

    return (header, body)

# Convert map into form encoded key=value string
def form_encode(form_data):
    ret = ""
    for key,value in form_data.items():
        if len(ret):
            ret += "&"
        ret += "%s=%s" % (key.replace(" ", "+"),value.replace(" ", "+"))
    return ret

# String -> HTTPResponse
# Get a path from the server
def get(path):
    return http_get(FAKEBOOK_HOST, path, retrieve_cookies())

# String Dict -> HTTPResponse
# Get a path from the server
def post(path, form_data):
    return http_post(FAKEBOOK_HOST, path, form_data, retrieve_cookies())
    
# Login
# Socket ->
def do_login(socket, username, password):
    global to_visit
    global cookie_store
    (header, login_page) = get(FAKEBOOK_HOME)
    store_cookies(header)
    token = cookie_store["csrftoken"]
    (header, body) = post(FAKEBOOK_LOGIN, {
        "csrfmiddlewaretoken": token, 
        "next": "/fakebook/", 
        "username": username, 
        "password": password 
    })
    success = header["response_code"] != "500"
    if success and header["Location"] != None:
        to_visit.append(header["Location"][0])
    return success

# Add the location from the redirect header to the queue
def handle_redirect(header):
    global to_visit
    to_visit.append(header["Location"][0])

# Entry point to the program
def main():
    args = parse_input()

    if not do_login(socket, args.username, args.password):
       print "Could not login" 
       exit(0)
    
    while len(to_visit) > 0:
        path = to_visit.popleft()
        print path
        visited.add(path)
        (header, body) = get(path)
        store_cookies(header)
        status = header["response_code"]
        if status == "200":
            parse_body(body)
        elif status == "301" or status == "302":
            handle_redirect(header, body)
        elif status == "500":
            to_visit.append(path)

    # not necessary, but nice to close the socket
    close_socket(socket)

# These 2 lines allow us to import this file into another file 
# and test individual components without running it
if __name__ == "__main__":
    main()
