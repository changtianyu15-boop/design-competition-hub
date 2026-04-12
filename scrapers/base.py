from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from models import Competition


class Scraper(ABC):
    name: str = "base"

    @abstractmethod
    def fetch(self) -> List[Competition]:
        raise NotImplementedError
