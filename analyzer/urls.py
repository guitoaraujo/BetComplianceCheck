from django.urls import path
from .views import upload_and_analyze, analysis_detail

urlpatterns = [
    path("", upload_and_analyze, name="analyze"),
    path("<int:pk>/", analysis_detail, name="analysis_detail"),
]
