from pydantic import BaseModel as PydanticModel

from .permission_type import PermissionType
 
class CommandPermission(PydanticModel):
    id: int
    cmd_txt: str
    need_power: int
