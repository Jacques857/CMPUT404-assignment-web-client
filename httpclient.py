#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
import select
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        startIndex = data.index(" ") + 1
        endIndex = startIndex + data[startIndex:].index(" ")
        return int(data[startIndex:endIndex])

    def get_headers(self, data):
        return None

    def get_body(self, data):
        startIndex = data.index("\r\n\r\n") + 4
        return data[startIndex:]
    
    def sendall(self, data):
        self.socket.sendall(data)
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # build a request
        request = build_get_request(url)

        # connect to the server
        self.connect(get_host(url), get_port(url))

        # make a GET request to the given url
        self.sendall(request.encode('utf-8'))

        # read the response
        response = self.recvall(self.socket)

        # close the connection
        self.close()

        # extract the status code and body of the response
        code = self.get_code(response)
        body = self.get_body(response)
        print("RESPONSE BODY:", body)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # build a request
        request = build_post_request(url, args)

        # connect to the server
        self.connect(get_host(url), get_port(url))

        # make a GET request to the given url
        self.sendall(request)

        # read the response
        response = self.recvall(self.socket)

        # close the connection
        self.close()

        # extract the status code and body of the response
        code = self.get_code(response)
        body = self.get_body(response)
        print("RESPONSE BODY:", body)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

def build_post_request(url, args):
    # request line
    request = "POST " + url + " HTTP/1.1\r\n"
    # headers
    request += "Host: " + get_host(url) + "\r\n"
    request += "User-Agent: CMPUT404/HTTPClient\r\n"
    request += "Connection: close\r\n"
    # if we are sending form data
    if args != None:
        request += "Content-Type: application/x-www-form-urlencoded\r\n"

    # content
    content = bytes("", 'utf-8')
    if args != None:
        for key in args:
            content += bytes(key, 'utf-8') + bytes("=", 'utf-8') + bytes(args[key], 'utf-8')
            content += bytes("&", 'utf-8')
        # remove the trailing &
        content = content[:len(content) - 1]
    
    # content length
    request += "Content-Length: " + str(len(content)) + "\r\n"

    # CRLF to end headers sections
    request += "\r\n"

    # append content
    request = bytes(request, 'utf-8')
    request += content
    request += bytes("\r\n", 'utf-8')

    return request

def build_get_request(url):
    # request line
    request = "GET " + url + " HTTP/1.1\r\n"
    # headers
    request += "Host: " + get_host(url) + "\r\n"
    request += "User-Agent: CMPUT404/HTTPClient\r\n"
    request += "Connection: close\r\n"
    # final CRLF
    request += "\r\n"

    return request

def get_host(url):
    startIndex = url.index("//") + 2
    if ":" in url[startIndex:]:
        endIndex = startIndex + url[startIndex:].index(":")
    elif "/" in url[startIndex:]:
        endIndex = startIndex + url[startIndex:].index("/")
    else:
        endIndex = len(url)
    host = url[startIndex:endIndex]
    return host

def get_port(url):
    hostStartIndex = url.index("//") + 2
    if ":" in url[hostStartIndex:]:
        startIndex = hostStartIndex + url[hostStartIndex:].index(":") + 1
        endIndex = startIndex + url[startIndex:].index("/")
        port = int(url[startIndex:endIndex])
    else:
        port = 80
    return port
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
