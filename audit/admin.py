from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Event)
admin.site.register(User)
admin.site.register(Calendar)
admin.site.register(Attendee)
admin.site.register(WatchChannel)