'''
import os
from flask import Flask

app = Flask(__name__)
@app.route('/')
def hello():
    return 'Hello, World!'
if __name__ =="__main__":
    app.run()
'''


from website import create_app
from waitress import serve
from simplejson import dumps
from website.config import ProductionConfig, DebugConfig
from sys import exit
from werkzeug.middleware.proxy_fix import ProxyFix

# Do NOT set BIND_HOST and BIND_PORT if using Docker
# will default to 0.0.0.0:80 and get exposed

app = create_app()
proxied = app
if app.config['PROXIED']:
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)

if __name__ == "__main__":
    if app.config['DEBUG']:
        app.run(host=app.config['BIND_HOST'], port=app.config['BIND_PORT'])
    else:
        serve(app, host=app.config['BIND_HOST'], port=app.config['BIND_PORT'])