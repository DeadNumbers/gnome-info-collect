#!/usr/bin/env python

#  PROJECT: gnome-info-collect
#  FILE:    server/server.py
#  LICENCE: GPLv3+
#  
#  Copyright 2021 vstanek <vstanek@redhat.com>

from http.server import HTTPServer, BaseHTTPRequestHandler

class RequestHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()
    
    def do_GET(self):
        self._set_response()
        self.wfile.write("Gnome-info-collect server v1\nStatus: Running\n".encode())

    def do_POST(self):
        length = int(self.headers['Content-Length']) # Gets the size of data
        data = self.rfile.read(length) # Gets the data
        
        # ~ Change to save the data into a file
        print(f"Recieved data: {data.decode()}")
        
        self._set_response()
        self.wfile.write("Request recieved\n".encode())

def main():
    PORT = 8080
    server = HTTPServer(('0.0.0.0', PORT), RequestHandler)
    print(f"Server running on port {PORT}")
    server.serve_forever()

if __name__ == '__main__':
    main()
