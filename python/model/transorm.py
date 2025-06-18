from typing import Any, Iterable

from sqlalchemy import select

from python.database.context_managger import transactional_session

from .auto_mapper import AutoMapper
from python.server.database import MAIN_SESSION


class Transform:

    @classmethod
    def get_dto(cls, source: type, destination: type, object_id: int, filter:Any=None, custom_mappings=None)-> Any:
        if not object_id and not filter:
            return None

        with transactional_session(MAIN_SESSION) as session:

            if filter is not None:
                source_object = session.scalars(select(source).filter(filter)).one_or_none()
            else:
                source_object = session.scalars(select(source).filter(source.id == object_id)).one_or_none()

            mapper = AutoMapper()
            mapper.add_mapping(source, destination, custom_mappings)

            return mapper.map(source_object, destination)

    @classmethod
    def get_db(cls, source: type, object_id: int | None, session_factory = MAIN_SESSION, existing_session = None)-> Any:
        if object_id is None:
            return None
        
        if existing_session:
            source_object = existing_session.scalars(select(source).filter(source.id == object_id)).one_or_none()
            return source_object
        
        with transactional_session(session_factory) as session:
            source_object = session.scalars(select(source).filter(source.id == object_id)).one_or_none()
            return source_object

    @classmethod
    def convert_db_to_dto(cls, source_object, destination, convert_to_dict: bool = False, custom_mappings=None) -> Any:
        if not source_object:
            return source_object

        src_type = type(source_object) 
        mapper = AutoMapper()


        if isinstance(source_object, Iterable):
            result: list[object] = []

            for obejct in source_object:
                src_data = obejct.to_dict() if convert_to_dict else obejct

                mapper.add_mapping(src_type, destination, custom_mappings)
                result.append(mapper.map(src_data, destination))

            return result

        else:
            src_data = source_object.to_dict() if convert_to_dict else source_object

            mapper.add_mapping(src_type, destination, custom_mappings)
            return mapper.map(src_data, destination)