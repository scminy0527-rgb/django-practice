from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import VideoJob
from .serializers import VideoJobSerializer
from .services import process_video


class VideoUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        """동영상 파일을 업로드하고 객체탐지 작업을 시작합니다."""
        video_file = request.FILES.get("video_file")
        if not video_file:
            return Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        job = VideoJob.objects.create(original_video=video_file)

        try:
            process_video(job.id)
        except Exception as e:
            job.status = "failed"
            job.save()
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = VideoJobSerializer(job)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        """최근 동영상 작업 목록을 조회합니다."""
        jobs = VideoJob.objects.all()[:5]
        serializer = VideoJobSerializer(jobs, many=True)
        return Response(serializer.data)


class VideoJobDetailAPIView(APIView):
    def get(self, request, job_id):
        """특정 동영상 작업의 상세 정보를 조회합니다."""
        job = get_object_or_404(VideoJob, id=job_id)
        serializer = VideoJobSerializer(job)
        return Response(serializer.data)
