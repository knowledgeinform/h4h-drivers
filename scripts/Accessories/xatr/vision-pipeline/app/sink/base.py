from __future__ import annotations

from abc import ABC, abstractmethod


class DetectionSink(ABC):
    @abstractmethod
    def create_msg(self, gps_data:dict, detection: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def publish(self, json_str: str) -> None:
        raise NotImplementedError