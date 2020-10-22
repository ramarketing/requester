from datetime import datetime
import json
import socket

from bs4 import BeautifulSoup
from flask import Flask, request, Response
import requests


app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    data = request.get_json()
    try:
        host = data['host']
        method = data.get('method', 'get')
        url = data['url']
    except KeyError:
        payload = dict(message='Invalid payload')
        return Response(
            json.dumps(payload), 400, mimetype='application/json'
        )

    start = datetime.now()
    try:
        ip_address = socket.gethostbyname(host)
        end = datetime.now()
        diff = int((end - start).microseconds / 1000)
    except (socket.gaierror, socket.timeout):
        ip_address = None
        diff = None

    try:
        resp = getattr(requests, method.lower())(
            allow_redirects=False,
            headers=data.get('headers', {}),
            params=data.get('params', {}),
            url=url
        )
    except (
        requests.ConnectionError,
        requests.ConnectTimeout,
        requests.HTTPError,
        requests.ReadTimeout,
        requests.Timeout,
        requests.TooManyRedirects,
        requests.exceptions.ChunkedEncodingError,
        requests.exceptions.ContentDecodingError,
    ) as err:
        response = dict(
            ip_address=ip_address,
            resolved_in=diff,
            content=err.__class__.__name__
        )
        return Response(
            json.dumps(response), 200, mimetype='application/json'
        )

    content = BeautifulSoup(resp.content, 'html.parser')
    content = content.html

    response = dict(
        ip_address=ip_address,
        resolved_in=diff,
        status_code=resp.status_code,
        response_headers=dict(resp.headers),
        elapsed=int(resp.elapsed.microseconds / 1000),
        content=str(content)
    )
    return Response(
        json.dumps(response), 200, mimetype='application/json'
    )
