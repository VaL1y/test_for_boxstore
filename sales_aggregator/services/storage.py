from typing import List
from models.sale import Sale


class Storage:
    def __init__(self):
        self._sales: List[Sale] = []

    def add(self, sales: List[Sale]):
        self._sales.extend(sales)

    def list(self) -> List[Sale]:
        return self._sales


storage = Storage()