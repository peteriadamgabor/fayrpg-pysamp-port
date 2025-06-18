from dataclasses import dataclass
from typing import Any

@dataclass
class MaterialText:
    material_index: int
    text: str
    material_size: int = 90
    font_face: str = "Arial"
    font_size: int = 24
    bold: bool = True
    font_color: int = 0xFFFFFFFF
    back_color: int = 0
    text_alignment: int = 0

    @staticmethod
    def from_dict(obj: Any) -> "MaterialText":
        _material_index = int(obj.get("material_index"))
        _text = str(obj.get("text"))
        _material_size = int(obj.get("material_size", 90))
        _font_face = str(obj.get("font_face", "Arial"))
        _font_size = int(obj.get("font_size", 24))
        _bold = bool(obj.get("bold", True))
        _font_color = int(obj.get("font_color", 0xFFFFFFFF))
        _back_color = int(obj.get("back_color", 0))
        _text_alignment = int(obj.get("text_alignment", 0))
        
        return MaterialText(
            material_index=_material_index,
            text=_text,
            material_size=_material_size,
            font_face=_font_face,
            font_size=_font_size,
            bold=_bold,
            font_color=_font_color,
            back_color=_back_color,
            text_alignment=_text_alignment
        )
