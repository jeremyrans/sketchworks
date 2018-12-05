"""
sketcher
"""
import math

import settings


class Sketcher(object):
    MAX_X = 500  # distance between upper corners of drawing boundary (i.e. steppers or guides)
    MAX_Y = 400

    def __init__(self, arduino):
        self.arduino = arduino
        self.x, self.y, self.z = (0, 0, 1)
        self.zero_x, self.zero_y = (0, 0)
        self.a, self.b = self.get_a_b(0.0, 0.0)
        self.error_a_steps, self.error_b_steps = (0.0, 0.0)
        self.set_zero(settings.zero_offset_x, settings.zero_offset_y)
        self.zero()

    @staticmethod
    def get_a_b(x, y):
        h = settings.max_x
        a = math.sqrt(x ** 2 + y ** 2)
        b = math.sqrt((h - x) ** 2 + y ** 2)
        return a, b

    @staticmethod
    def get_step_delta_and_error(curr_mm, dest_mm, prev_error):
        step_delta = (dest_mm - curr_mm) / settings.mm_per_step + prev_error
        step_delta_rounded = round(step_delta)
        error = step_delta - step_delta_rounded
        return int(step_delta_rounded), error

    def get_step_deltas(self, x, y):
        x += self.zero_x
        y += self.zero_y
        dest_a, dest_b = self.get_a_b(x, y)
        delta_a, self.error_a_steps = self.get_step_delta_and_error(self.a, dest_a, self.error_a_steps)
        delta_b, self.error_b_steps = self.get_step_delta_and_error(self.b, dest_b, self.error_b_steps)
        self.a, self.b = dest_a, dest_b
        return delta_a, delta_b

    def move_delta(self, x=None, y=None, z=None):
        self.x = self.x + x if x else self.x
        self.y = self.y + y if y else self.y
        self.z = self.z + z if z else self.z
        self.move()

    def move(self, x=None, y=None, z=None, preview=False, update_queue=True):
        z_changed = False
        if z is not None and z != self.z:
            z_changed = True
        self.x = x if x is not None else self.x
        self.y = y if y is not None else self.y
        self.z = z if z is not None else self.z

        delta_a, delta_b = self.get_step_deltas(self.x, self.y)
        print "x: %s, y: %s, z: %s" % (self.x, self.y, self.z)

        if update_queue:
            settings.websocket_queue.put(self.to_coordinate_dict())

        if not preview and self.arduino:
            self.arduino.write("%d;%d;%d;%d;" % (delta_a, delta_b, self.z, settings.speed))

        return delta_a, delta_b, z_changed

    def set_zero(self, zero_x, zero_y):
        self.zero_x = zero_x
        self.zero_y = zero_y
        dest_a, dest_b = self.get_a_b(zero_x, zero_y)
        self.a, self.b = dest_a, dest_b
        self.x, self.y, self.z = (0, 0, 1)

    def zero(self, preview=False):
        self.move(z=1, preview=preview)  # lift pen
        self.move(x=0, y=0, preview=preview)  # move to home

    def to_coordinate_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
        }
