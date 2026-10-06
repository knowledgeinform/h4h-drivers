from __future__ import annotations

import uuid
import json

from app.sink.base import DetectionSink


class MockSink(DetectionSink):
    def create_msg(self, gps_data:dict, detection: dict):
        return json.dumps({
            "uid" : str(uuid.uuid1()),
            "latitude" : gps_data["messageData"]["lat"],
            "longitude" : gps_data["messageData"]["lon"],
            "callsign" : detection["label"],
            "sender_callsign" : "Vision_Pipeline",
        })

    def publish(self, json_str: str) -> None:
        print(json_str)