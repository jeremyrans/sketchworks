""" main """
import fileinput
import logging
import re
import webbrowser
import thread
from paste import httpserver
import settings
from sketcher import Sketcher
import webapp2

from routes import ROUTES
import websocket


config = {
    'webapp2_static.static_file_path': 'static',
    'globals': {
        'uri_for': webapp2.uri_for
    }
}
web_app = webapp2.WSGIApplication(routes=ROUTES, config=config, debug=True)

def main():
    # configure logging
    logging.basicConfig(level=logging.INFO)

    # launch websocket handler in another thread
    thread.start_new_thread(websocket.websocket_main, ())

    # launch main wsgi app
    logging.info("Sketchworks started")
    webbrowser.open("http://127.0.0.1:6060")
    settings.sketcher = Sketcher(None)
    httpserver.serve(web_app, host='127.0.0.1', port='6060')
    logging.info("Sketchworks terminated")

if __name__ == "__main__":
    main()
