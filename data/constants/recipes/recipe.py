from typing import List

from data.constants.items import Item
from util.quantity import Quantity


class Recipe:

    def __init__(self, inputs: List[Quantity[Item]], output: Quantity[Item]):
        self.inputs = inputs
        self.output = output
