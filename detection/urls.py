from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.upload_video, name="upload_video"),
    path("jobs/", views.list_jobs, name="list_jobs"),
    path("jobs/<int:job_id>/", views.get_job_status, name="get_job_status"),
    path("jobs/<int:job_id>/original/", views.serve_original_video, name="serve_original_video"),
    path("jobs/<int:job_id>/video/", views.serve_result_video, name="serve_result_video"),
    path("jobs/<int:job_id>/download/", views.download_result_video, name="download_result_video"),
]
