import re

from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Regexp

PLATE_NUMBER_PATTERN = re.compile(r"([a-zA-Z]{2,3}[\s-]?(\d{2,5}))|((\d{4})[\s-]?[a-zA-Z]{2})")


class VehicleRegistrationScheduleForm(FlaskForm):
    license_plate = StringField(
        "License Plate",
        validators=[
            InputRequired(),
            Regexp(PLATE_NUMBER_PATTERN, message="Does not match any accepted license plate format"),
        ],
        render_kw={"placeholder": "Enter License Plate", "class": "form-control"},
    )
    recaptcha = RecaptchaField()
    get_schedule = SubmitField("Get Schedule", render_kw={"class": "btn btn-primary btn-block"})
