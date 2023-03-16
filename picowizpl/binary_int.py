from dataclasses import dataclass
from typing import List
from .compiler import *

@dataclass
class BinaryInt:
    wires: List[Wire]

