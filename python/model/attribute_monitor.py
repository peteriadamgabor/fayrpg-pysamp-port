from typing import override
from abc import abstractmethod, ABC


class AttributeMonitor(ABC):
    def __init__(self, force_update_properties: set[str] = None, not_watched_properties: set[str] = None) -> None:
        if not_watched_properties is None:
            not_watched_properties = set()

        if force_update_properties is None:
            force_update_properties = set()

        self.attr_change: bool = False
        self._force_update_properties: set[str] = force_update_properties
        self._not_watched_properties: set[str] = not_watched_properties
        self.under_init = False

    @override
    def __setattr__(self, name, value) -> None:
        if name == "attr_change":
            super().__setattr__(name, value)
            return

        if hasattr(self, name) and name not in self._not_watched_properties:
            if getattr(self, name) != value:
                super().__setattr__(name, value)

                if name in self._force_update_properties:
                    self.update_database_entity(True)
                else:
                    super().__setattr__("attr_change", True)
        else:
            super().__setattr__(name, value)


    @abstractmethod
    def update_database_entity(self, is_force_update: bool = False) -> None:
        raise NotImplementedError()
