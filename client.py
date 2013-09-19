#!/usr/bin/python

from optparse import OptionParser 
import socket
import ssl

FAKEBOOK_HOST = "cs5700.ccs.neu.edu"
FAKEBOOK_HOME = "/accounts/login/?next=/fakebook/"

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
def http_get(socket, host, path, cookies=[]):
    header =  "GET %s HTTP/1.1\n" % path
    header += "Host: %s\n" % host
    header += "\n"

    sent_bytes = send_data(socket, header)

    response = split_http(recv_data(socket))
    header = parse_header(response[0])
    body = response[1]

    return (header, body)

# Entry point to the program
def main():
    args = parse_input()

    # Create a connection to the server
    socket = open_socket(FAKEBOOK_HOST, 80, False)
    

    login_page = http_get(socket, FAKEBOOK_HOST, FAKEBOOK_HOME)
    print login_page

    # Listen for data and respond appropriately

    # not necessary, but nice to close the socket
    close_socket(socket)

# These 2 lines allow us to import this file into another file 
# and test individual components without running it
if __name__ == "__main__":
    main()
