from webapp2 import Route
from handlers import StaticFileHandler


ROUTES = [
    Route('/', handler='handlers.Settings', name='settings'),
    Route('/interactive/', handler='handlers.Interactive', name='interactive'),
    Route('/gcode/', handler='handlers.GCode', name='gcode'),
    Route('/gcode/estimate/', handler='handlers.EstimateGcode', name='gcode'),
    Route('/demo/', handler='handlers.Demo', name='demo'),
    Route('/disconnect-socket/', handler='handlers.DisconnectSocket', name='disconnect-socket'),
    Route('/flush-socket/', handler='handlers.FlushSocket', name='flush-socket'),
    (r'/static/(.+)', StaticFileHandler)
]
