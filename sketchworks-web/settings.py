import math
from Queue import Queue

# globals
max_x = 2400.0
max_y = 1016.0
bobbin_radius = 8.2
steps_per_revolution = 1600
bobbin_circumference = 2 * math.pi * bobbin_radius
mm_per_step = bobbin_circumference / steps_per_revolution
zero_offset_x = 381.0
zero_offset_y = 203.0
arduino_port = None
arduino = None
sketcher = None
websocket_host = "ws://localhost:6061/"
websocket_queue = Queue()
speed = 400


def recompute_mm_per_step():
    global mm_per_step
    mm_per_step = bobbin_circumference / steps_per_revolution
