from django.contrib import admin
from .models import VideoJob


@admin.register(VideoJob)
class VideoJobAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "detected_count", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("id",)
    readonly_fields = ("detected_count", "detection_summary", "created_at", "updated_at")
    fieldsets = (
        ("Video Files", {"fields": ("original_video", "result_video")}),
        ("Status", {"fields": ("status",)}),
        ("Detection Results", {"fields": ("detected_count", "detection_summary")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
