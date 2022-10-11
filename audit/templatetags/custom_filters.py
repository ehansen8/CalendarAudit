from django import template
import calendar
from datetime import datetime

register = template.Library()


@register.filter
def duration(value) -> str:
    if not value:
        return None
    try:
        seconds = int(value.total_seconds())

        h = seconds // 3600
        m = (seconds - h * 3600) // 60
        return f"{h} hrs {m} min"
    except:
        return None


@register.filter
def month_name(month_number):
    return calendar.month_name[month_number]


@register.filter
def week_date(week: int, year: int):
    """Return the date of the first day (monday-indexed) of the given week"""
    return datetime.fromisocalendar(year, week, 1).date()
