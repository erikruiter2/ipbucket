
from flask import Flask
import sys,logging
import settings
#logging.basicConfig(stream=sys.stderr)
from wsgi import wsgi_app
from logging.handlers import RotatingFileHandler

app = Flask(__name__ , static_url_path='')
app.register_blueprint(wsgi_app)
app.debug = True
if __name__ == "__main__":
    handler = RotatingFileHandler('ipbucket.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host = settings.WSGI_host , port = settings.WSGI_port)
