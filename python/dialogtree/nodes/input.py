# InputNode.py
from typing import Union

from ._base import BaseNode
from python.utils.enums.dialog_style import DialogStyle
from pysamp.dialog import Dialog
from pysamp.player import Player


class InputNode(BaseNode):
    def __init__(
        self,
        node_name: str,
        content: str,
        button_1: str,
        button_2: str,
        title: str,
        display: str = "",
        is_password: bool = False,
    ):
        super().__init__(node_name, content, button_1, button_2, title)
        self.display = display
        self.set_dialog_style(DialogStyle.PASSWORD if is_password else DialogStyle.INPUT)
        self.save_input = True
        self.set_save_input(True)

    def add_child(self, child: Union["BaseNode", None]) -> None:
        if len(self.get_children()) >= 1:
            raise RuntimeError("InputNode can only have 1 or 0 children!")
        super().add_child(child)

    def show(self, player: Player) -> None:
        generated_content = self.content_creator(
            player, *self._get_custom_args(self.content_creator_parameters, self.content_creator_node_parameters)
        )

        if not self.content and not generated_content:
            generated_content = "No elements"

        content = self.content + generated_content
        self.dialogs = self._create_dialogs(content)
        self.dialogs[0].show(player)

    def _create_dialogs(self, content: str) -> list[Dialog]:
        return [
            Dialog.create(self._dialog_style, title, body, self.button_1, self.button_2, self._handler)
            for title, body in self._prepare_content(content)
        ]
