from ._base import BaseNode
from python.utils.enums.dialog_style import DialogStyle


class MessageNode(BaseNode):
    def __init__(self, node_name: str, content: str, button_1: str, button_2: str, title: str, display:str = ""):
        super().__init__(node_name, content, button_1, button_2, title)

        self._dialog_style = DialogStyle.MSGBOX
        self.display = display

