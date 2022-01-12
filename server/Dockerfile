# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /app

RUN pip3 install jsonschema

COPY server.py server.py
COPY data.schema.json data.schema.json

CMD [ "python3", "server.py" ]