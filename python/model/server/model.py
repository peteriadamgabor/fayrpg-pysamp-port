from dataclasses import dataclass


@dataclass
class Model:
    base_id: int
    new_id: int
    dff: str
    txd: str

