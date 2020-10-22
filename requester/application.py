from datetime import datetime
import json
import socket

from bs4 import BeautifulSoup
from flask import Flask, request
import requests


app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    try:
        host = request.form['host']
        method = request.form.get('method', 'get')
        url = request.form['url']
    except KeyError:
        return 'Invalid payload', 400

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
            headers=request.form.get('headers', {}),
            params=request.form.get('params', {}),
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
        return json.dumps(response)

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
    return json.dumps(response)
