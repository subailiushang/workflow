from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name="login"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('register', views.register, name="register"),
    path('logout', views.logout, name="logout"),
    path('base', views.base, name="base"),
    path('dailyReports', views.dailyReports, name="dailyReports"),
    path('del_dailyReports', views.del_dailyReports, name="del_dailyReports"),
    path('projects', views.projects, name="projects"),

]
