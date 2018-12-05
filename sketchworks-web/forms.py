from wtforms import Form, SubmitField, FloatField, SelectField, IntegerField


class SettingsForm(Form):
    max_x = FloatField(label='Max X (mm)')
    max_y = FloatField(label='Max Y (mm)')
    bobbin_radius = FloatField(label='Bobbin Radius (mm)')
    offset_x = FloatField(label='X Zero Offset (mm)')
    offset_y = FloatField(label='Y Zero Offset (mm)')
    port = SelectField(label='Arduino Port')
    speed = IntegerField(label='Speed (steps/sec, 400-3600 recommended)')
    submit = SubmitField('Submit')
