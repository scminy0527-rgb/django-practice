from django.apps import AppConfig


class DetectionConfig(AppConfig):
    name = "detection"

    def ready(self):
        from ultralytics import YOLO
        import os

        model_path = os.path.join(os.path.dirname(__file__), "yolov8n.pt")

        if not os.path.exists(model_path):
            print("[YOLO] Downloading YOLOv8n model (first time only)...")
            self.model = YOLO("yolov8n.pt")
            self.model.save(model_path)
        else:
            print("[YOLO] Loading YOLOv8n model from cache...")
            self.model = YOLO(model_path)

        print("[YOLO] Model loaded successfully!")
