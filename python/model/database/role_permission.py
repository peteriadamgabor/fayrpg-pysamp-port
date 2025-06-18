from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import  relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base
from .permission_type import PermissionType

class RolePermission(Base):
   __tablename__ = 'role_permissions'
   __allow_unmapped__ = True

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
   permission_type_id: Mapped[int] = mapped_column(ForeignKey("permission_types.id"))
   permission_type: Mapped[PermissionType] = relationship("PermissionType")
   power: Mapped[int] = mapped_column(Integer)
