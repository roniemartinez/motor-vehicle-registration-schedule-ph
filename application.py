import logging
import os
import sys
from calendar import monthrange
from datetime import datetime
from typing import List, Tuple, Union

from flask import Flask, render_template, request
from pytz import timezone

from custom_calendar import CustomHTMLCalendar
from forms import PLATE_NUMBER_PATTERN, VehicleRegistrationScheduleForm

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

application = Flask(__name__)

application.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
application.config["RECAPTCHA_PUBLIC_KEY"] = os.getenv("RECAPTCHA_PUBLIC_KEY")
application.config["RECAPTCHA_PRIVATE_KEY"] = os.getenv("RECAPTCHA_PRIVATE_KEY")
application.config["RECAPTCHA_ENABLED"] = int(os.getenv("RECAPTCHA_ENABLED", 0))


def get_day_groups(year: int, month: int) -> List[List[int]]:
    day_groups: List[List[int]] = [[], [], [], []]
    for i in range(1, monthrange(year, month)[1] + 1):
        try:
            day_groups[(i - 1) // 7].append(i)
        except IndexError:
            day_groups[3].append(i)
    return day_groups


def get_schedule(license_plate: str) -> Tuple[List[int], int, int]:
    a, b = PLATE_NUMBER_PATTERN.match(license_plate).groups()[1::2]  # type: ignore
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


@application.route("/", methods=["GET", "POST"])
def motor_vehicle_registration_schedule() -> str:
    form = VehicleRegistrationScheduleForm()

    if not application.config["RECAPTCHA_ENABLED"]:
        del form.recaptcha

    has_schedule: Union[str, bool] = False
    days: List[int] = []
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
