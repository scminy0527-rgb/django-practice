from django.urls import path
from .views import VideoUploadAPIView, VideoJobDetailAPIView

urlpatterns = [
    path("videos/", VideoUploadAPIView.as_view(), name="video_upload"),
    path("videos/<int:job_id>/", VideoJobDetailAPIView.as_view(), name="video_detail"),
]
