from __future__ import annotations

import json


def serialize_detection_message(message: dict) -> str:
    return json.dumps(message, separators=(",", ":"), ensure_ascii=False)