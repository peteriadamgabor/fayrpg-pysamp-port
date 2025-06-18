from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.attributes import instance_state
from sqlalchemy import select

from python.database import transactional_session
from python.server.database import MAIN_SESSION


class Base(DeclarativeBase):
    __abstract__ = True

    def to_dict(self, max_depth: int = 2, current_depth: int = 0):
        def serialize(value):
            if isinstance(value, Base):
                if current_depth < max_depth:
                    return value.to_dict(max_depth, current_depth + 1)
                
                elif hasattr(value, 'id'):
                    return {"id": getattr(value, "id"), "__class__": value.__class__.__name__}
                
                else:
                    return {"__class__": value.__class__.__name__}
                
            elif isinstance(value, list):
                return [serialize(item) for item in value]
            
            else:
                return value

        result = {}
        state = instance_state(self)
        if state.detached:
            return None
        for attr in state.attrs.keys():
            result[attr] = serialize(getattr(self, attr))
        return result