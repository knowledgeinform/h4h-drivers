from __future__ import annotations

from models.yolov3.yolo import YoloNet
from app.detector.dto import Detection


class YoloDetector:
    def __init__(
        self,
        confidence: float = 0.5,
        classes_of_interest: list[str] | None = None,
    ) -> None:
        
        # set up network
        self.model = YoloNet(
            config="models/yolov3/yolov3.cfg", 
            weights="models/yolov3/yolov3.weights", 
            labels="models/yolov3/coco.names", 
            confidence=confidence, 
            nms=0.3)
        self.confidence = confidence
        self.classes_of_interest = set(classes_of_interest or [])
        self.model_name = "YOLOv3"

        print("Classes of Interest:", self.classes_of_interest)

    def predict(self, frame):
        detections = []
        # get inference and filter by class
        results = self.model.getDetections(frame)

        # sort through the bounding Boxes objects
        for detection in results:
            # unpack
            bbox, conf, label, id, _ = detection

            # filter by label
            if not label in self.classes_of_interest:
                continue

            # convert bounding box from xywh to xyxy
            x,y,w,h = bbox
            ex = x + w
            ey = y + h
            bbox = [x,y,ex,ey]

            # add to detections
            detections.append(Detection(
                label=label,
                class_id=id,
                confidence=conf,
                bbox_xyxy=bbox
            ))
        return detections
