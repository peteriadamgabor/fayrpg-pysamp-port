from pydantic import BaseModel as PydanticModel

from python.model.registrymixin import RegistryMixin

class Interior(PydanticModel, RegistryMixin[int, "Interior"]):
   id: int
   name: str
   x: float
   y: float
   z: float
   a: float
   interior: int

   def model_post_init(self, __context):
      self.add_registry_item(self.id, self)

   def get_id(self) -> int:
      return self.id