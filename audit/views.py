from ast import Num
from django.shortcuts import redirect, render
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from .calendar_manager import CalendarManager
from .reports import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


@login_required
def index(request: HttpRequest) -> HttpResponse:
    user = request.user
    m = CalendarManager(user)
    m.sync_events(full_sync=False)

    rb = ReportBuilder(user, num_months=3)

    time_per_month = rb.get_time_per_month()
    min_meetings, max_meetings = rb.get_most_and_least_meetings()
    light_week, busy_week = rb.get_busiest_weeks()
    avg_meetings_week = rb.get_avg_meetings_week()
    avg_time_meetings_week = rb.get_avg_time_meetings_week()
    top_collaborators = rb.get_top_collaborators(num_people=3)
    time_recruiting = rb.get_time_recruiting()
    
    context = {
        "time_per_month": time_per_month,
        "min_meetings": min_meetings,
        "max_meetings": max_meetings,
        "light_week": light_week,
        "busy_week": busy_week,
        "avg_meetings_week": avg_meetings_week,
        "avg_time_meetings_week": avg_time_meetings_week,
        "top_collaborators": top_collaborators,
        "time_recruiting": time_recruiting,
    }
    return render(request, "index.html", context=context)


def home(request: HttpRequest) -> HttpResponse:
    user = request.user
    if user.is_authenticated:
        return redirect("audit:index")

    return redirect("login")


@csrf_exempt
def watch(request) -> HttpResponse:

    calendar_email = request.headers.get("X-Goog-Channel-Token")
    state = request.headers.get("X-Goog-Resource-State")

    # This Skips Sync notifications
    if state == "exists":
        user = User.objects.get(primary_calendar__email=calendar_email)
        m = CalendarManager(user=user).sync_events(full_sync=False)

    return HttpResponse(status=200)
