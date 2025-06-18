from pydantic import BaseModel as PydanticModel

from .permission_type import PermissionType

class RolePermission(PydanticModel):
   id: int
   role_id: int
   permission_type: PermissionType
   power: int
