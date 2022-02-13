from calendar import HTMLCalendar
from typing import List


class CustomHTMLCalendar(HTMLCalendar):
    cssclass_month_head = "month text-center"
    cssclass_month = "month table table-responsive table-sm d-flex justify-content-center"

    def __init__(self, days: List[int]) -> None:
        super(CustomHTMLCalendar, self).__init__(firstweekday=6)
        self.days = days

    def formatday(self, day: int, weekday: int) -> str:
        if day == 0:
            return super(CustomHTMLCalendar, self).formatday(day, weekday)
        classes = " ".join([self.cssclasses[weekday], "table-danger" if day in self.days else ""])
        return '<td class="%s">%d</td>' % (classes, day)
