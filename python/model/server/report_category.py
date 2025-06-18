from dataclasses import dataclass, field
from typing import override, Any
from python.model.registrymixin import RegistryMixin

@dataclass
class ReportCategory(RegistryMixin[str, "ReportCategory"]):
    id: int
    code: str
    name: str
    color: str
    is_deletabel: bool
    is_visible: bool
    order: int
    admins: dict[int, Any] = field(default_factory=dict)

    @override
    def get_id(self) -> str:
        return self.code
