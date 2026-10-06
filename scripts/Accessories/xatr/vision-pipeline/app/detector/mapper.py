from __future__ import annotations

from app.detector.dto import Detection



def yolo_results_to_detections(results, frame) -> list[Detection]:
    detections: list[Detection] = []

    if not results:
        return detections

    result = results[0]
    names = result.names

    if result.boxes is None:
        return detections

    for box in result.boxes:
        cls_id = int(box.cls.item())
        confidence = float(box.conf.item())
        xyxy = box.xyxy[0].tolist()
        label = str(names.get(cls_id, str(cls_id)))

        detections.append(
            Detection(
                label=label,
                class_id=cls_id,
                confidence=confidence,
                bbox_xyxy=[int(v) for v in xyxy],
            )
        )

    return detections



    