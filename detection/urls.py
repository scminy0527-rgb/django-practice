from django.urls import path
from . import views

urlpatterns = [
    path("", views.upload_view, name="upload_view"),
    path("result/<int:job_id>/", views.result_view, name="result_view"),
]
