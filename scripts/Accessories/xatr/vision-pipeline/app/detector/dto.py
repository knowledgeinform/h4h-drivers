from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Detection:
    label: str
    class_id: int
    confidence: float
    bbox_xyxy: list[int]

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "class_id": self.class_id,
            "confidence": round(float(self.confidence), 4),
            "bbox_xyxy": [int(v) for v in self.bbox_xyxy],
        }