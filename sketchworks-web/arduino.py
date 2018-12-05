"""
arduino
"""
from serial import Serial
from serial.tools import list_ports


class Arduino(object):
    def __init__(self, port):
        self.serial = Serial(port, 115200)
        print "serial initialized"

        input = self.serial.read() or ''
        if input == 'A':
            self.serial.write('A')
            print "handshake successful"
        else:
            print "no handshake byte, continuing assuming things are OK"

    def read(self):
        input = self.serial.readline().strip()
        print "read '%s'" % input
        return input

    def write(self, to_write):
        print "write '%s'" % to_write
        self.serial.write(to_write)
        return self.read()


def get_ports():
    available_ports = dict(enumerate([port[0] for port in list_ports.comports()]))
    return available_ports
