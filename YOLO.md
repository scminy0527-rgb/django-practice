# 프로젝트: YOLO 객체 탐지 Django 샘플

## 목표

샘플 동영상을 업로드하면 YOLO가 사람/차량을 탐지해
바운딩박스가 그려진 결과 영상을 웹에서 바로 재생할 수 있는 시스템

## 기술 스택

- Python 3.11+
- Django 4.x
- ultralytics (YOLOv8n)
- OpenCV (cv2) - 프레임 추출 및 바운딩박스 렌더링
- SQLite (Django 내장 DB)
- Celery 없음 (동기 처리)

## 앱 구조

detection/
models.py - VideoJob 모델 (업로드 영상, 결과 영상, 상태, 탐지 수)
views.py - 업로드 / 처리 / 결과 조회
urls.py
apps.py - 앱 시작 시 YOLO 모델 1회 로드
templates/
upload.html - 업로드 폼
result.html - 결과 영상 재생 + 탐지 정보

## 핵심 구현 규칙

1. YOLO 모델은 DetectionConfig.ready()에서 1회만 로드
2. 처리 흐름: 업로드 → OpenCV 프레임 분해 → YOLO 추론
   → 바운딩박스 그리기 → 영상 재합성 → DB 저장
3. 탐지 클래스 필터: person, car, truck, bus, bicycle
4. 결과 영상 저장 경로: media/results/
5. UI는 Django 템플릿으로 구현
   - 업로드 페이지: 파일 선택 + 제출 버튼
   - 결과 페이지: <video> 태그로 결과 영상 재생
     - 탐지된 객체 수 / 클래스별 통계 표시
6. Django Admin에 VideoJob 등록해서 관리 가능하게

## VideoJob 모델 필드

- original_video: 원본 영상 (FileField)
- result_video: 결과 영상 (FileField)
- status: pending / processing / done / failed
- detected_count: 총 탐지 수 (IntegerField)
- detection_summary: 클래스별 통계 (JSONField)
- created_at / updated_at
