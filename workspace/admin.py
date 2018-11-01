from django.contrib import admin
from .models import MyUser, DailyReports, Project

# Register your models here.


admin.site.register(MyUser)
admin.site.register(DailyReports)
admin.site.register(Project)
