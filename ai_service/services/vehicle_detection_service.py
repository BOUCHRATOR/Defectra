from ultralytics import YOLO


class VehicleDetectionService:

    def __init__(self):

        print("Loading YOLO model...")

        self.model = YOLO("yolo26n.pt")

        print("YOLO model loaded.")

    def detect_vehicle(self, image_path, confidence=0.25):

        results = self.model.predict(
            source=image_path,
            conf=confidence
        )

        vehicles = []

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(box.cls[0])

                class_name = result.names[class_id]

                # COCO : 2 = car
                if class_id != 2:
                    continue

                score = float(box.conf[0])

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                vehicles.append({
                    "type": "car",
                    "confidence": score,
                    "bbox": {
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2
                    }
                })

        return vehicles