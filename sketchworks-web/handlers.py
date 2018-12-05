import fileinput
import logging
import mimetypes
import os

from forms import SettingsForm
import gcode
import webapp2
from webapp2_extras import jinja2

import arduino
import settings
import sketcher


def jinja2_factory(app):
    logging.info("template path: %s", os.path.join(os.path.dirname(__file__), 'templates'))
    j = jinja2.Jinja2(app, {'template_path': os.path.join(os.path.dirname(__file__), 'templates')})
    j.environment.globals.update({
        'uri_for': webapp2.uri_for
    })
    return j

class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(factory=jinja2_factory, app=self.app)

    def redirect(self, uri, permanent=False, abort=True, code=None, body=None):
        super(BaseHandler, self).redirect(uri, permanent=permanent, abort=abort, code=code, body=body)

    def render_response(self, _template, **context):
        base_context = {
            'websocket_host': settings.websocket_host,
            'max_x': settings.max_x,
            'max_y': settings.max_y,
            'zero_offset_x': settings.zero_offset_x,
            'zero_offset_y': settings.zero_offset_y,
            'sketcher_initialized': bool(settings.sketcher.arduino)
        }
        base_context.update(context)
        rv = self.jinja2.render_template(_template, **base_context)
        self.response.write(rv)


class Settings(BaseHandler):
    def get(self):
        form = SettingsForm()
        form.max_x.data = settings.max_x
        form.max_y.data = settings.max_y
        form.bobbin_radius.data = settings.bobbin_radius
        form.offset_x.data = settings.zero_offset_x
        form.offset_y.data = settings.zero_offset_y
        form.speed.data = settings.speed
        form.port.choices = arduino.get_ports().items()
        form.port.data = settings.arduino_port
        context = {
            'settings_form': form,
        }
        return self.render_response('settings.html', **context)

    def post(self):
        form = SettingsForm(self.request.POST)
        settings.max_x = form.data['max_x'] or settings.max_x
        settings.max_y = form.data['max_y'] or settings.max_y
        settings.bobbin_radius = form.data['bobbin_radius'] or settings.bobbin_radius
        settings.zero_offset_x = form.data['offset_x'] or settings.zero_offset_x
        settings.zero_offset_y = form.data['offset_y'] or settings.zero_offset_y
        settings.arduino_port = form.data['port'] or settings.arduino_port
        settings.speed = form.data['speed'] or settings.speed
        settings.recompute_mm_per_step()

        if form.data['port']:
            if settings.arduino:
                settings.arduino.serial.close()
            settings.arduino = arduino.Arduino(arduino.get_ports()[int(settings.arduino_port)])
            if settings.sketcher:
                settings.sketcher.arduino = settings.arduino
            else:
                settings.sketcher = sketcher.Sketcher(settings.arduino)
        settings.sketcher.set_zero(settings.zero_offset_x, settings.zero_offset_y)

        return self.get()


class Demo(BaseHandler):
    def get(self):
        self.render_response('demo.html')


class Interactive(BaseHandler):
    def get(self):
        self.render_response('interactive.html')

    def post(self):
        x = self.request.get('x')
        y = self.request.get('y')
        z = self.request.get('z')
        x = float(x) if x else None
        y = float(y) if y else None
        z = float(z) if z else None
        settings.sketcher.move_delta(x=x, y=y, z=z)


class GCode(BaseHandler):
    def get(self):
        self.render_response('gcode.html')

    def post(self):
        file_path = self.request.get('file_path')
        preview = self.request.get('preview') == 'true'
        scale = float(self.request.get('scale'))
        x_offset = float(self.request.get('x_offset'))
        y_offset = float(self.request.get('y_offset'))
        print "submitted file_path", file_path
        input_file = fileinput.input(file_path)
        gcode.run_gcode(input_file,
                        preview=preview,
                        scale=scale,
                        x_offset=x_offset,
                        y_offset=y_offset)


class EstimateGcode(BaseHandler):
    def post(self):
        file_path = self.request.get('file_path')
        scale = float(self.request.get('scale'))
        x_offset = float(self.request.get('x_offset'))
        y_offset = float(self.request.get('y_offset'))
        print "submitted file_path for estimation", file_path
        input_file = fileinput.input(file_path)
        self.response.write(gcode.estimate(input_file,
                            scale=scale,
                            x_offset=x_offset,
                            y_offset=y_offset))


class DisconnectSocket(webapp2.RequestHandler):
    def get(self):
        settings.websocket_queue.put('QUIT')


class FlushSocket(webapp2.RequestHandler):
    def get(self):
        settings.websocket_queue.put('FLUSH')


class StaticFileHandler(webapp2.RequestHandler):
    def get(self, path):
        abs_path = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), 'static'), path))
        if os.path.isdir(abs_path):
            self.response.set_status(403)
            return
        try:
            f = open(abs_path, 'rb')
            self.response.headers.add_header('Content-Type', mimetypes.guess_type(abs_path)[0])
            self.response.out.write(f.read())
            f.close()
        except:
            self.response.set_status(404)
