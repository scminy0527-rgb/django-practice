import os
import cv2
import numpy as np
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps
from django.core.files.base import ContentFile
from .models import VideoJob


DETECTION_CLASSES = {"person", "car", "truck", "bus", "bicycle"}


def get_yolo_model():
    detection_config = apps.get_app_config("detection")
    return detection_config.model


@require_http_methods(["GET", "POST"])
def upload_view(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("video_file")
        if not uploaded_file:
            return JsonResponse({"error": "No file provided"}, status=400)

        job = VideoJob.objects.create(
            original_video=uploaded_file,
            status="pending"
        )

        try:
            process_video_task(job.id)
        except Exception as e:
            job.status = "failed"
            job.save()
            return JsonResponse({"error": str(e)}, status=500)

        return redirect("result_view", job_id=job.id)

    jobs = VideoJob.objects.all()[:5]
    return render(request, "detection/upload.html", {"jobs": jobs})


def process_video_task(job_id):
    job = VideoJob.objects.get(id=job_id)
    job.status = "processing"
    job.save()

    try:
        model = get_yolo_model()
        input_path = job.original_video.path
        output_dir = os.path.join(os.path.dirname(input_path), "..", "results")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"result_{job_id}.mp4")

        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        detection_summary = {}
        frame_count = 0
        total_detections = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame, conf=0.5)

            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    cls_name = model.names[cls_id]

                    if cls_name.lower() not in DETECTION_CLASSES:
                        continue

                    detection_summary[cls_name] = detection_summary.get(cls_name, 0) + 1
                    total_detections += 1

                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = float(box.conf[0])

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"{cls_name} {confidence:.2f}"
                    cv2.putText(
                        frame,
                        label,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2,
                    )

            out.write(frame)
            frame_count += 1

        cap.release()
        out.release()

        job.detected_count = total_detections
        job.detection_summary = detection_summary
        job.status = "done"

        with open(output_path, "rb") as f:
            job.result_video.save(
                f"result_{job_id}.mp4",
                ContentFile(f.read()),
                save=True
            )

        os.remove(output_path)

    except Exception as e:
        job.status = "failed"
        job.save()
        raise e


def result_view(request, job_id):
    job = get_object_or_404(VideoJob, id=job_id)
    return render(request, "detection/result.html", {"job": job})
