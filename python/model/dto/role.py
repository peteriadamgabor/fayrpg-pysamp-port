from pydantic import BaseModel as PydanticModel

from .role_permission import RolePermission as RolePermissionDTO

class Role(PydanticModel):
    id: int
    name: str
    code: str
    is_visible: bool
    permissions: list[RolePermissionDTO]
    power: int
