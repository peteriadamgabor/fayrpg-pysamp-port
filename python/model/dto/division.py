from pydantic import BaseModel as PydanticModel

from python.model.registrymixin import RegistryMixin

class Division(PydanticModel, RegistryMixin[int, "Division"]):
    id: int
    name: str 
    acronym: str
    is_leader: bool
    is_recruit: bool

    def model_post_init(self, __context):
        self.add_registry_item(self.id, self)

    def get_id(self) -> int:
        return self.id