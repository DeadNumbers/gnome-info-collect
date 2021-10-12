#!/usr/bin/env python

from http.server import HTTPServer, BaseHTTPRequestHandler

class RequestHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()
    
    def do_GET(self):
        self._set_response()
        self.wfile.write("Hello world!".encode())

    def do_POST(self):
        length = int(self.headers['Content-Length']) # Gets the size of data
        data = self.rfile.read(length) # Gets the data
        
        # ~ Change to save the data into a file
        print(f"Recieved data: {data.decode()}")
        
        self._set_response()
        self.wfile.write("Request recieved\n".encode())

def main():
    PORT = 12345
    server = HTTPServer(('', PORT), RequestHandler)
    print(f"Server running on port {PORT}")
    server.serve_forever()

if __name__ == '__main__':
    main()
