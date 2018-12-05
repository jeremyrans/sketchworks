import json
import logging
import time
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer
import settings


FLUSH_SECONDS = 1.0  # every X seconds, push out all accumulated coords

def websocket_main():
    logging.info("starting websocket server")
    server = SimpleWebSocketServer('', 6061, CoordinateFeeder)
    server.serveforever()
    logging.info("websocker server terminated")


class CoordinateFeeder(WebSocket):
    def handleConnected(self):
        print self.address, 'connected'

    def handleClose(self):
        print self.address, 'closed'

    def handleMessage(self):
        data = str(self.data)
        coordinates = []
        if data == 'STATUS' and settings.sketcher:
            self.sendMessage(json.dumps([settings.sketcher.to_coordinate_dict()]))
            settings.websocket_queue.queue.clear()
        last_flush = time.time()
        while True:
            data = settings.websocket_queue.get()
            if str(data) == 'QUIT':
                settings.websocket_queue.queue.clear()
                self.sendClose()
                raise Exception("received client close")
            elif str(data) != 'FLUSH':
                coordinates.append(data)

            if str(data) == 'FLUSH' or last_flush + FLUSH_SECONDS < time.time():
                last_flush = time.time()
                self.sendMessage(json.dumps(coordinates))
                coordinates = []
