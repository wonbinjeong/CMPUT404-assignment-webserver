#  coding: utf-8 
from genericpath import isfile
import socketserver
import os.path

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


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip().decode().split("\r\n")
        # print ("Got a request of: %s\n" % self.data)

        request = self.data[0].split(" ")
        self.method = request[0]
        self.url = request[1]
        self.http = request[2]
        self.root = "www"

        # check for GET
        if (self.method != "GET"):
            response = self.send_response(405)
            self.request.sendall(bytearray(response,'utf-8'))
            return
        
        # check urls
        # check if there is a / in the end, as well as if it has an extension
        if (self.url[-1] == "/" and "." not in self.url):
            self.url += "index.html"

            # file exists
            if (os.path.isfile(self.root + self.url)):
                response = self.send_response(200, self.url.split(".")[1])
                f = open(self.root + self.url).read()
                self.request.sendall(bytearray(response + f,'utf-8'))
            else: # file does not exist
                response = self.send_response(404)
                self.request.sendall(bytearray(response,'utf-8'))
            return
        elif (self.url[-1] != "/" and "." not in self.url):
            # does not end path
            self.url += "/"
            response = self.send_response(301)
            self.request.sendall(bytearray(response,'utf-8'))
            return
        else:
            file = self.url.split(".")

            # no extension
            if (len(file) != 2):
                response = self.send_response(404)
                self.request.sendall(bytearray(response,'utf-8'))
                return

            file_extension = file[1]

            # does not end path
            if (self.url[-1] == "/"):
                self.url = self.url[:-1]

            # print(self.root + self.url)
            if (os.path.isfile(self.root + self.url)):
                response = self.send_response(200, file_extension)
                f = open(self.root + self.url).read()
                self.request.sendall(bytearray(response + f,'utf-8'))
            else:
                response = self.send_response(404)
                self.request.sendall(bytearray(response,'utf-8'))

        # self.request.sendall(bytearray("OK",'utf-8'))

    def send_response(self, response, file_extension=""):
        header = "{} ".format(self.http)

        if (response == 200):
            header += "200 OK\n"
        elif (response == 301):
            header += "301 Moved Permanently\n"
            header += "Location: http://127.0.0.1:8080{}\n".format(self.url)
        elif (response == 404):
            header += "404 Path Not Found\n"
        elif (response == 405):
            header += "405 Method Not Allowed\n"

        c_type = "text/html"
        if (file_extension == "css" or file_extension == "css/"):
            c_type = "text/css"

        header += "Content-Type: {}\n".format(c_type)

        return header

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
