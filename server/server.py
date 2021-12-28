#!/usr/bin/env python

#  PROJECT: gnome-info-collect
#  FILE:    server/server.py
#  LICENCE: GPLv3+
#
#  Copyright 2021 vstanek <vstanek@redhat.com>

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from time import time
import json
import jsonschema


class RequestHandler(BaseHTTPRequestHandler):
    def _set_OK_response(self):
        self.send_response(200)
        self.send_header('content-type', 'text/plain')
        self.end_headers()

    def _set_invalid_data_response(self):
        self.send_response(400)
        self.send_header('content-type', 'text/plain')
        self.end_headers()

    def _process_post_data(self):
        length = int(self.headers['Content-Length'])  # Gets the size of data
        data = self.rfile.read(length).decode()  # Gets the data

        # ~ Debug
        # ~ print(f"Recieved data:\n{data}")
        try:
            self._validate_post_data(data)
        except (ValueError, jsonschema.exceptions.ValidationError):
            raise

        # ~ Get to parent directory and create a file in the folder 'data'
        with open(
            str(Path(__file__).parent.parent.absolute()) +
            "/data/" + f"data_{time()}.json",
            "w"
        ) as f:
            f.write(data)

    def _validate_post_data(self, data):
        try:
            with open(
                str(Path(__file__).with_name("data.schema.json")),
                "r"
            ) as f_schema:
                json_schema = json.load(f_schema)
                json_data = json.loads(data)

                jsonschema.validate(instance=json_data, schema=json_schema)

        except (ValueError, jsonschema.exceptions.ValidationError):
            raise

    def do_GET(self):
        self._set_OK_response()
        self.wfile.write(
            "Gnome-info-collect server v1\nStatus: Running\n".encode()
        )

    def do_POST(self):
        try:
            self._process_post_data()
        except (ValueError, jsonschema.exceptions.ValidationError):
            self._set_invalid_data_response()
            self.wfile.write("Error: Invalid data received\n".encode())
            raise

        self._set_OK_response()
        self.wfile.write("Data received successfully\n".encode())


def main():
    PORT = 8080
    server = ThreadingHTTPServer(('0.0.0.0', PORT), RequestHandler)
    print(f"Server running on port {PORT}")
    server.serve_forever()


if __name__ == '__main__':
    main()
