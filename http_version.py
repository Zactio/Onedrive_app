import os
from flask import Flask, request
import flask
APP = flask.Flask(__name__, template_folder='static/templates')
APP.debug = True
APP.secret_key = 'development'

@APP.route('/')
def hello():
     return request.environ.get('SERVER_PROTOCOL')


ssl_dir: str = os.path.dirname(__file__).replace('src', 'ssl')
key_path: str = os.path.join(ssl_dir, 'ssl/server.key')
crt_path: str = os.path.join(ssl_dir, 'ssl/server.crt')
ssl_context: tuple = (crt_path, key_path)


if __name__ == "__main__":
    APP.run('0.0.0.0', 8000, debug=True, ssl_context=ssl_context)
