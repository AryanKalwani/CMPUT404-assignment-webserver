#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# References used
# https://www.geeksforgeeks.org/python-os-path-isdir-method/
# https://note.nkmk.me/en/python-os-exists-isfile-isdir/
# https://www.w3schools.com/python/python_file_open.asp
# https://stackoverflow.com/questions/70817388/trying-to-send-http-response-message-over-tcp-in-python


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.data = self.data.decode().split(" ")
        if self.data[0]=="GET":
            self.handle_get()
        else:
            # Sending 405 for all other request methods
            self.request.sendall(bytearray('HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/html; charset=utf-8\r\n\r\n','utf-8'))
            self.request.sendall('405 - This method is not allowed. Only GET method is allowed.'.encode('utf-8'))

    def handle_get(self):
        # checking if the request param is a directory
        directory = os.path.isdir('www' + self.data[1])
        # checking if the request param is a file
        file = os.path.isfile('www' + self.data[1])

        # checking if the directory/file being accessed is not upwards of the current directory
        if "../" in self.data[1]:
            self.request.sendall(bytearray('HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=utf-8\r\n\r\n', 'utf-8'))
            self.request.sendall('404 - Page that you requested was not found'.encode('utf-8'))
        elif directory:
            if self.data[1][-1]!='/':
                # Redirecting to correct Location
                self.request.sendall(bytearray('HTTP/1.1 301 Moved Permanently\r\nLocation: {}\nContent-Type: text/plain; charset=utf-8\r\n\r\n'.format(self.data[1]+"/"), 'utf-8'))
            else:
                # Returning content of index.html by default with status OK
                f = open("www/{}/index.html".format(self.data[1]), "r")
                self.request.sendall(bytearray('HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n', 'utf-8'))
                self.request.sendall(f.read().encode('utf-8'))
                f.close()
        elif file:
            # Returning content of requested file with status OK
            f = open("www/{}".format(self.data[1]), "r")
            file_type = self.data[1].split(".")[1]
            self.request.sendall(bytearray('HTTP/1.1 200 OK\r\nContent-Type: text/{}; charset=utf-8\r\n\r\n'.format(file_type), 'utf-8'))
            self.request.sendall(f.read().encode('utf-8'))
            f.close()
        if not file and not directory:
            # If not a valid file or directory, returning 404 Not Found
            self.request.sendall(bytearray('HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=utf-8\r\n\r\n', 'utf-8'))
            self.request.sendall('404 - Page that you requested was not found'.encode('utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
