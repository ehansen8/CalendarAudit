from dateutil.relativedelta import relativedelta
from .models import User
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractWeek
from django.db.models import Sum, Count, Avg, F, Q
from .utils import DateUtil

class ReportBuilder:
    def __init__(self, user: User, num_months=3) -> None:
        self.user = user
        self.tz = user.primary_calendar.timezone
        self.num_months = num_months
    
    def _filter_by_range(self, max_date_type: str="month"):
        d = DateUtil(tz=self.tz)
        time_max = None
        
        if max_date_type == "month":
            time_max = d.this_month
        elif max_date_type == "week":
            time_max = d.this_week
        elif max_date_type == "day":
            time_max = d.today
        
        time_min = d.this_month - relativedelta(months=self.num_months)

        events = self.user.primary_calendar.events
        return events.filter(start__range=(time_min, time_max), all_day=False)

    def get_time_per_month(self):
        """Returns the total time spent in meetings per Month for the last x months up to the the start of the current month"""

        events = self._filter_by_range("month")

        results = (
            events.annotate(month=ExtractMonth("start"))
            .values("month")
            .annotate(time=Sum("duration"))
            .order_by("month")
        )
        return results


    def get_most_and_least_meetings(self):
        """Returns Most and Least # of meetings per Month for the last x months up to the the start of the current month
        in the form of (min#, max#)"""

        events = self._filter_by_range("month")
        results = (
            events.annotate(month=ExtractMonth("start"))
            .values("month")
            .annotate(count=Count("pk"))
            .order_by("count")
        )
        return results.first(), results.last()


    def get_busiest_weeks(self):
        """Returns Most and Least time spent in meetings per week for the last x months up to the last full-week
        in the form of (min#, max#)"""

        events = self._filter_by_range("week")
        results = (
            events.annotate(week=ExtractWeek("start"))
            .annotate(year=ExtractYear("start"))
            .values("week", "year")
            .annotate(time=Sum("duration"))
            .order_by("time")
        )
        return results.first(), results.last()


    def get_avg_meetings_week(self):
        """Returns Avg # of meetings per week for the last x months up to the last full-week"""

        events = self._filter_by_range("week")
        results = (
            events.annotate(week=ExtractWeek("start"))
            .values("week")
            .annotate(count=Count("pk"))
            .aggregate(avg=Avg("count"))
        )
        return results


    def get_avg_time_meetings_week(self):
        """Returns Avg time of meetings per week for the last x months up to the last full-week"""

        events = self._filter_by_range("week")
        results = (
            events.annotate(week=ExtractWeek("start"))
            .values("week")
            .annotate(time=Sum("duration"))
            .aggregate(avg=Avg("time"))
        )
        return results


    def get_top_collaborators(self, num_people: int):
        """Return the top x # of people you have met with in the last y months up to today"""
        events = self._filter_by_range("day")
        results = (
            events.annotate(email=F("attendees__email"))
            .exclude(email=self.user.primary_calendar.email)
            .values("email")
            .annotate(count=Count("email"))
            .order_by("-count")
        )
        return results[:num_people]


    def get_time_recruiting(self):
        """Return the time spent recruiting or conducting interviews
        Filters on if a Meeting Title [summary] contains certain keywords"""

        keywords = ["recruiting", "interview"]
        kw_filter = Q()
        for kw in keywords:
            kw_filter |= Q(summary__icontains=kw)

        events = self._filter_by_range("day")
        results = events.filter(kw_filter).aggregate(time=Sum("duration"))
        return results
