from typing import override
from dataclasses import dataclass
from python.model.registrymixin import RegistryMixin

from python.model.dto import BusinessType as BusinessTypeDTO

@dataclass
class Interior(RegistryMixin[int, "Interior"]):

    id: int
    x: float
    y: float
    z: float
    a: float
    interior: int
    price: int
    business_type: BusinessTypeDTO
    zone: "InteriortDynamicZone"

    def __post_init__(self):
        self.add_registry_item(self.id, self)

    @override
    def get_id(self) -> int:
        return self.id