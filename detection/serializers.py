from rest_framework import serializers
from .models import VideoJob


class VideoJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoJob
        fields = ['id', 'original_video', 'result_video', 'status', 'detected_count', 'detection_summary', 'created_at', 'updated_at']
        read_only_fields = ['id', 'result_video', 'status', 'detected_count', 'detection_summary', 'created_at', 'updated_at']


class VideoJobDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoJob
        fields = ['id', 'original_video', 'result_video', 'status', 'detected_count', 'detection_summary', 'created_at', 'updated_at']
        read_only_fields = ['id', 'result_video', 'detected_count', 'detection_summary', 'created_at', 'updated_at']
