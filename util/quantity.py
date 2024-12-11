from typing import TypeVar, Generic

T = TypeVar('T')


class Quantity(Generic[T]):
    def __init__(self, content: T, quantity: int):
        self.content = content
        self.quantity = quantity

    def __str__(self):
        return str(self.content)
