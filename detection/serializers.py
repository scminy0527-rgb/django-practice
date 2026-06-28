from rest_framework import serializers
from .models import VideoJob


class VideoJobSerializer(serializers.ModelSerializer):
    original_video_url = serializers.SerializerMethodField()
    result_video_url = serializers.SerializerMethodField()

    class Meta:
        model = VideoJob
        fields = [
            'id',
            'status',
            'original_video_url',
            'result_video_url',
            'detected_count',
            'detection_summary',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'status',
            'detected_count',
            'detection_summary',
            'created_at',
            'updated_at',
        ]

    def get_original_video_url(self, obj):
        request = self.context.get('request')
        if obj.original_video:
            video_url = f"/detection/jobs/{obj.id}/original/"
            return request.build_absolute_uri(video_url) if request else video_url
        return None

    def get_result_video_url(self, obj):
        request = self.context.get('request')
        if obj.result_video:
            video_url = f"/detection/jobs/{obj.id}/video/"
            return request.build_absolute_uri(video_url) if request else video_url
        return None


class VideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoJob
        fields = ['original_video']

    def create(self, validated_data):
        return VideoJob.objects.create(
            original_video=validated_data['original_video'],
            status='pending'
        )
