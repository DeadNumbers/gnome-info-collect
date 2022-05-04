#!/usr/bin/env python3

#  PROJECT: gnome-info-collect
#  FILE:    server/server.py
#  LICENCE: GPLv3+
#
#  Copyright 2021 vstanek <vstanek@redhat.com>

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import date
import json
import jsonschema
import os


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
            id = self._validate_post_data(data)
        except (ValueError, jsonschema.exceptions.ValidationError):
            raise

        # ~ Create a file in folder of today's date
        dir_path = f"/app/data/{str(date.today())}"
        file_path = f"{dir_path}/{id}.json"

        if not Path(dir_path).exists():
            os.mkdir(dir_path)

        if Path(file_path).exists():
            raise FileExistsError
        else:
            with open(file_path, "w") as f:
                f.write(data)

    def _validate_post_data(self, data) -> str:
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

        return json_data["Unique ID"]

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
        except FileExistsError:
            self._set_OK_response()
            self.wfile.write("Your data was already collected\n".encode())
        else:
            self._set_OK_response()
            self.wfile.write("Data received successfully\n".encode())


def main():
    PORT = 8080
    server = ThreadingHTTPServer(('0.0.0.0', PORT), RequestHandler)
    print(f"Server running on port {PORT}")
    server.serve_forever()


if __name__ == '__main__':
    main()
