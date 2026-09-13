from dataclasses import dataclass
from typing import List


@dataclass
class Defect:

    type: str
    confidence: float
    severity: str


@dataclass
class VehicleDetection:

    plate: str
    brand: str
    model: str
    year: int
    inspection_date: str

    defects: List[Defect]