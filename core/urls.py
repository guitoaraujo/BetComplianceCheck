from django.urls import path
from .views import home, terms, privacy

urlpatterns = [
    path("", home, name="home"),
    path("terms/", terms, name="terms"),
    path("privacy/", privacy, name="privacy"),
]
