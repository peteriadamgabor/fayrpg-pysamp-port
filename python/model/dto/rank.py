from typing import Optional, Union
from pydantic import BaseModel as PydanticModel

from python.model.registrymixin import RegistryMixin, D, T


class Rank(PydanticModel, RegistryMixin[int, "Rank"]):
    id: int
    order: int
    fraction_id: int
    division_id: Optional[int]
    name: str

    def model_post_init(self, __context):
        self.add_registry_item(self.id, self)

    def get_id(self) -> int:
        return self.id

    @classmethod
    def from_registry(cls, obj: Union[D, T]) -> T:
        pass
