import logging
import re
import settings
from sketcher import Sketcher


def run_gcode(input_file, preview=False, scale=1.0, x_offset=0.0, y_offset=0.0):
    for line in input_file:
        parsed_instruction = parse_gcode_instruction(line)
        if not parsed_instruction:
            continue
        x, y, z = parsed_instruction
        if x is not None:
            x *= scale
            x += x_offset
        if y is not None:
            y *= scale
            y += y_offset
        y = (settings.max_y - y) if y else None
        settings.sketcher.move(x=x, y=y, z=z, preview=preview)
    input_file.close()
    settings.sketcher.zero(preview=preview)


def parse_gcode_instruction(gcode):
    # remove comments
    gcode = re.sub(r'\([^)]*\)', '', gcode)
    gcode = gcode.replace(';', '')  # strip out semicolons
    parts = []
    # throw away anything before the first G instruction
    for i, letter in enumerate(gcode):
        if letter == 'G':
            parts = gcode.upper()[i:].split()
            break
    if not parts:
        return

    if parts[0] not in frozenset(['G0', 'G1', 'G00', 'G01']):
        return {}

    coordinates = {}
    for part in parts[1:]:
        try:
            key = part[0].lower()
            value = float(part[1:])
            coordinates[key] = value
        except Exception:
            logging.info('failure to parse %s', part)

    x = coordinates.get('x')
    y = coordinates.get('y')
    z = coordinates.get('z')
    return x, y, z


def estimate(input_file, scale=1.0, x_offset=0.0, y_offset=0.0):
    total_steps = 0
    z_changes = 0
    sketcher = Sketcher(None)
    for line in input_file:
        parsed_instruction = parse_gcode_instruction(line)
        if not parsed_instruction:
            continue
        x, y, z = parsed_instruction
        if x is not None:
            x *= scale
            x += x_offset
        if y is not None:
            y *= scale
            y += y_offset
        y = (settings.max_y - y) if y else None
        delta_x, delta_y, z_changed = sketcher.move(x=x, y=y, z=z, preview=True, update_queue=False)
        total_steps += max(delta_x, delta_y)
        if z_changed:
            z_changes += 1
    input_file.close()
    return (total_steps / settings.speed) + (.2 * z_changes)  # 200ms pause per z change

