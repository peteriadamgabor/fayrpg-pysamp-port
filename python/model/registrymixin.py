from functools import wraps
from typing import Any, TypeVar, Generic, ClassVar, Union
from abc import ABC, abstractmethod, abstractclassmethod
from _collections_abc import dict_items

D = TypeVar('D')
T = TypeVar('T')

class RegistryMixin(Generic[D, T], ABC):
    _registry: ClassVar[dict[D, T]] = {} # type: ignore

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._registry = {}

    @abstractmethod
    def get_id(self) -> D:
        raise NotImplementedError()

    @classmethod
    def from_registry(cls, obj: Union[D, T]) -> T:
        raise NotImplementedError()
        
    @classmethod
    def add_registry_item(cls, id: D, obj: T) -> None:
        cls._registry[id] = obj

    @classmethod
    def get_registry_items(cls) -> list[T]:
        return list(cls._registry.values())

    @classmethod
    def get_registry_items_with_keys(cls):
        return cls._registry.items()

    @classmethod
    def get_registry_item(cls, id: D | None) -> T | None:
        return cls._registry.get(id, None) # type: ignore

    @classmethod
    def remove_from_registry(cls, obj: T) -> None:
        cls._registry.pop(obj.get_id(), None) # type: ignore

    @classmethod
    def using_registry(cls, func) -> Any:
        @wraps(func)
        def from_registry(*args, **kwargs):
            args = list(args)
            args[0] = cls.from_registry(args[0])
            return func(*args, **kwargs)

        return from_registry
