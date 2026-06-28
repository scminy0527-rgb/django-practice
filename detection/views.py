from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.http import FileResponse
from .models import VideoJob
from .services import process_video
from .serializers import VideoJobSerializer, VideoUploadSerializer


@api_view(['POST'])
def upload_video(request):
    """비디오 파일 업로드 및 처리 시작"""
    serializer = VideoUploadSerializer(data=request.data)
    if serializer.is_valid():
        job = serializer.save()
        try:
            process_video(job.id)
        except Exception as e:
            job.status = "failed"
            job.save()
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        response_serializer = VideoJobSerializer(job, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_job_status(request, job_id):
    """특정 job의 상태 및 결과 조회"""
    try:
        job = VideoJob.objects.get(id=job_id)
    except VideoJob.DoesNotExist:
        raise NotFound({"error": f"Job {job_id} not found"})

    serializer = VideoJobSerializer(job, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def list_jobs(request):
    """최근 job 목록 조회"""
    jobs = VideoJob.objects.all()[:20]
    serializer = VideoJobSerializer(jobs, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def serve_original_video(request, job_id):
    """원본 비디오 스트리밍"""
    try:
        job = VideoJob.objects.get(id=job_id)
    except VideoJob.DoesNotExist:
        raise NotFound({"error": f"Job {job_id} not found"})

    if not job.original_video:
        return Response(
            {"error": "Original video not available"},
            status=status.HTTP_404_NOT_FOUND
        )

    file_response = FileResponse(
        open(job.original_video.path, 'rb'),
        content_type='video/mp4'
    )
    file_response['Content-Disposition'] = 'inline'
    return file_response


@api_view(['GET'])
def serve_result_video(request, job_id):
    """처리된 비디오 스트리밍"""
    try:
        job = VideoJob.objects.get(id=job_id)
    except VideoJob.DoesNotExist:
        raise NotFound({"error": f"Job {job_id} not found"})

    if not job.result_video:
        return Response(
            {"error": "Result video not available"},
            status=status.HTTP_404_NOT_FOUND
        )

    file_response = FileResponse(
        open(job.result_video.path, 'rb'),
        content_type='video/mp4'
    )
    file_response['Content-Disposition'] = 'inline'
    return file_response


@api_view(['GET'])
def download_result_video(request, job_id):
    """처리된 비디오 다운로드"""
    try:
        job = VideoJob.objects.get(id=job_id)
    except VideoJob.DoesNotExist:
        raise NotFound({"error": f"Job {job_id} not found"})

    if not job.result_video:
        return Response(
            {"error": "Result video not available"},
            status=status.HTTP_404_NOT_FOUND
        )

    file_response = FileResponse(
        open(job.result_video.path, 'rb'),
        content_type='video/mp4'
    )
    file_response['Content-Disposition'] = f'attachment; filename="result_{job_id}.mp4"'
    return file_response
