#!/usr/bin/python

from optparse import OptionParser 
import socket
import ssl

cookie_store = {
    'csrftoken': None,
    'sessionid': None
}

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
def retrieve_cookie():
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
def open_socket(server, port, use_ssl):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if use_ssl:
        s = ssl.wrap_socket(s)
    s.settimeout(5)
    s.connect((server, port))
    return s

# Close the socket
def close_socket(socket):
    socket.close()

# Parse the socket data
def parse_data(data):
    return data.split(' ')

# Receive data from the socket
def recv_data(socket):
    return socket.recv(4096)

# Send data on the socket
def send_data(socket, data):
    return socket.send(data)

# Entry point to the program
def main():
    args = parse_input()

    # Create a connection to the server
    socket = open_socket(args.server, args.port, args.ssl)

    # Listen for data and respond appropriately
    response = parse_data(recv_data(socket))
    while response:
        response = None

    # not necessary, but nice to close the socket
    close_socket(socket)

# These 2 lines allow us to import this file into another file 
# and test individual components without running it
if __name__ == "__main__":
    main()
