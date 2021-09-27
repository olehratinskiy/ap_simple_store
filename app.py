from flask import Flask
from wsgiref.simple_server import make_server
from greeting import api

app = Flask(__name__)

with make_server('', 5000, app) as server:
    app.register_blueprint(api, url_prefix="/api/v1")
    server.serve_forever()

