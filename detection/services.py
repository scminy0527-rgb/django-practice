import os
import cv2
from django.apps import apps
from django.core.files.base import ContentFile
from django.conf import settings
from .models import VideoJob


DETECTION_CLASSES = {"person", "car", "truck", "bus", "bicycle"}


def get_yolo_model():
    detection_config = apps.get_app_config("detection")
    return detection_config.model


def process_video(job_id):
    """동영상 파일에서 객체 탐지를 수행하고 결과 동영상을 생성합니다."""
    job = VideoJob.objects.get(id=job_id)
    job.status = "processing"
    job.save()

    temp_output_path = None
    try:
        model = get_yolo_model()
        input_path = job.original_video.path

        # Django media 경로에 직접 저장
        results_dir = os.path.join(settings.MEDIA_ROOT, "results", "videos")
        os.makedirs(results_dir, exist_ok=True)
        temp_output_path = os.path.join(results_dir, f"temp_result_{job_id}.mp4")

        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 호환성이 높은 H.264 코덱 사용
        fourcc = cv2.VideoWriter_fourcc(*"H264")
        out = cv2.VideoWriter(temp_output_path, fourcc, fps, (width, height))

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

        # 파일 저장 확인
        if not os.path.exists(temp_output_path):
            raise Exception(f"Output video file not created: {temp_output_path}")

        file_size = os.path.getsize(temp_output_path)
        if file_size == 0:
            raise Exception(f"Output video file is empty: {temp_output_path}")

        # 최종 파일명으로 이동
        final_filename = f"result_{job_id}.mp4"
        final_path = os.path.join(settings.MEDIA_ROOT, "results", "videos", final_filename)

        if os.path.exists(final_path):
            os.remove(final_path)

        os.rename(temp_output_path, final_path)

        # Django FileField에 상대 경로 설정
        relative_path = os.path.join("results", "videos", final_filename)
        job.result_video.name = relative_path

        job.detected_count = total_detections
        job.detection_summary = detection_summary
        job.status = "done"
        job.save()

    except Exception as e:
        job.status = "failed"
        job.save()

        # 실패 시 임시 파일 정리
        if temp_output_path and os.path.exists(temp_output_path):
            os.remove(temp_output_path)

        raise e
