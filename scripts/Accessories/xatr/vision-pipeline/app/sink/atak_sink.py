from __future__ import annotations

import uuid

from app.sink.base import DetectionSink
import atakcots as tak


class AtakSink(DetectionSink):
    def __init__(self, address: str, port: int):
            self.address = address
            self.port = port

    def create_msg(self, gps_data:dict, detection: dict):
         return tak.CotConfig(
            uid=str(uuid.uuid1()),
            latitude=gps_data["lat"][1],
            longitude=gps_data["lon"][1],
            callsign=detection["label"],
            sender_callsign="Vision_Pipeline",
        )
        
    def publish(self, cot_msg: tak.CotConfig) -> None:
        tak.push_cot(cot_msg, self.address, self.port)