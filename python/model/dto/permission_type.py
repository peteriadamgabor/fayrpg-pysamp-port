from pydantic import BaseModel as PydanticModel

class PermissionType(PydanticModel):
   id: int
   name: str
   code: str
   description: str | None
