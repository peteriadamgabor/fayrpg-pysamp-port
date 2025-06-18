from typing import Union, override

from pysamp.player import Player
from pysamp.dialog import Dialog

from ._base import BaseNode
from python.utils.enums.dialog_style import DialogStyle

class ConfirmNode(BaseNode):
    def __init__(self, node_name: str, content: str, button_1: str, button_2: str, title: str, display:str = ""):
        super().__init__(node_name, content, button_1, button_2, title)

        self.__dialog_style = DialogStyle.MSGBOX
        self.close_in_end: bool = True
        self.display = display

    def add_child(self, child: Union["BaseNode", None]) -> None:
        if len(self._children) == 1:
            raise RuntimeError("Confirm Node can only have 1 or 0 child!")

        self._children.append(child)
        if child is not None:
            child._parent = self

    def show(self, player: Player) -> None:
        generated_content = self.content_creator(player, self._get_custom_args(self.content_creator_parameters, self.content_creator_node_parameters))

        if not self.content and not generated_content:
            generated_content = "No elements"

        content = self.content + generated_content
        self.dialogs = self._create_dialogs(content)
        self.dialogs[0].show(player)
    
    @override
    def _create_dialogs(self, content: str) -> list[Dialog]:
        return [
            Dialog.create(self.__dialog_style, title, body, self.button_1, self.button_2, self._handler)
            for title, body in self._prepare_content(content)
        ]