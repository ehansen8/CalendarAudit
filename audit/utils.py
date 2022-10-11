from calendar import week
from datetime import datetime, timezone, tzinfo
import pytz


def to_rfc(dt: datetime) -> str:
    """Convert datetime to RFC 3339 compliant string"""

    # Google API Doesn't like "+0000" utc offset, so convert to utc then remove tz info
    try:
        dt = dt.astimezone(pytz.utc)
    except:
        pass
    dt = dt.replace(tzinfo=None)
    formatted = dt.isoformat() + "Z"
    return formatted


def to_dt(time: str, tz: str, as_date=False) -> datetime:
    s = None
    if as_date:
        s = datetime.strptime(time, "%Y-%m-%d")
    else:
        s = datetime.strptime(time[:-6], "%Y-%m-%dT%H:%M:%S")

    return pytz.timezone(tz).localize(s)


def get_start_of_month(time: datetime) -> datetime:
    pass


class DateUtil:
    """Date utility class primarily focused on getting the start of days/weeks/months
    starting at the first of each (e.g. first day of the month @ midnight, etc) in the form of datetimes instead of just dates. Uses local timezone
    """

    def __init__(self, dt: datetime = None, tz: str = None) -> None:
        today = dt.date() if dt else datetime.now().date()
        self.year = today.year
        self.month = today.month
        self.week = today.isocalendar().week
        self.day = today.day
        self.tz = pytz.timezone(tz)

    @property
    def today(self) -> datetime:
        dt = datetime(year=self.year, month=self.month, day=self.day)
        return self.tz.localize(dt)

    @property
    def this_week(self) -> datetime:
        dt = datetime.fromisocalendar(year=self.year, week=self.week, day=1)
        return self.tz.localize(dt)

    @property
    def this_month(self) -> datetime:
        dt = datetime(year=self.year, month=self.month, day=1)
        return self.tz.localize(dt)
