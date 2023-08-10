from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path('chart/<uuid:pk>', views.chart, name='chart'),
    path("signin", views.signin, name="signin"),
    path("signup", views.signup, name="signup"),
    path("settings", views.settings, name="settings"),
    path("logout", views.logout, name="logout"),
    path("follow-chart/<uuid:pk>", views.follow_chart, name="follow-chart"),
    path("search", views.search, name="search"),
]

