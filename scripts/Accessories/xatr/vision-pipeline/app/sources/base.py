from __future__ import annotations

from abc import ABC, abstractmethod


class FrameSource(ABC):
    @abstractmethod
    def open(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def read(self):
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError