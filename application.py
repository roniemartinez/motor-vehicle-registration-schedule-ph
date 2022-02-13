import logging
import os
import re
import sys
from calendar import HTMLCalendar, monthrange
from datetime import datetime

from flask import Flask, render_template, request
from flask_wtf import FlaskForm, RecaptchaField
from pytz import timezone
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Regexp

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

application = Flask(__name__)

application.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

plate_number_pattern = re.compile(r"([a-zA-Z]{2,3}[\s-]?(\d{2,5}))|((\d{4})[\s-]?[a-zA-Z]{2})")


def get_day_groups(year, month):
    day_groups = [[], [], [], []]
    for i in range(1, monthrange(year, month)[1] + 1):
        try:
            day_groups[(i - 1) // 7].append(i)
        except IndexError:
            day_groups[3].append(i)
    return day_groups


def get_schedule(license_plate):
    a, b = plate_number_pattern.match(license_plate).groups()[1::2]
    week_digit, month_digit = map(int, (a or b)[-2:])
    month = month_digit or 10
    week_index = dict(zip(range(10), [3, 0, 0, 0, 1, 1, 1, 2, 2, 3]))[week_digit]
    now = datetime.now(tz=timezone("Asia/Manila"))
    year = now.year if now.month <= month else now.year + 1
    day_groups = get_day_groups(year, month)
    days = [d for d in day_groups[week_index] if datetime(year, month, d).isoweekday() < 6]
    if now.month == month and all([now.day > day for day in days]):
        year += 1
        days = [d for d in day_groups[week_index] if datetime(year, month, d).isoweekday() < 6]
    return days, month, year


class VehicleRegistrationScheduleForm(FlaskForm):
    license_plate = StringField(
        "License Plate",
        validators=[
            InputRequired(),
            Regexp(plate_number_pattern, message="Does not match any accepted license plate format"),
        ],
        render_kw={"placeholder": "Enter License Plate", "class": "form-control"},
    )
    # recaptcha = RecaptchaField()
    get_schedule = SubmitField("Get Schedule", render_kw={"class": "btn btn-primary btn-block"})


class CustomHTMLCalendar(HTMLCalendar):
    cssclass_month_head = "month text-center"
    cssclass_month = "month table table-responsive table-sm d-flex justify-content-center"

    def __init__(self, days):
        super(CustomHTMLCalendar, self).__init__(firstweekday=6)
        self.days = days

    def formatday(self, day, weekday):
        if day == 0:
            # day outside month
            return '<td class="%s">&nbsp;</td>' % self.cssclass_noday
        else:
            classes = self.cssclasses[weekday] + " table-danger" if day in self.days else ""
            return '<td class="%s">%d</td>' % (classes, day)


@application.route("/", methods=["GET", "POST"])
def motor_vehicle_registration_schedule():
    form = VehicleRegistrationScheduleForm()
    has_schedule = False
    days = []
    if request.method == "POST" and form.validate_on_submit():
        try:
            days, month, year = get_schedule(form.license_plate.data)
            calendar = CustomHTMLCalendar(days=days)
            has_schedule = calendar.formatmonth(year, month)
        except AttributeError:
            has_schedule = False
    return render_template("index.html", form=form, has_schedule=has_schedule, days=days)


if __name__ == "__main__":
    application.run(host="0.0.0.0", threaded=True)
