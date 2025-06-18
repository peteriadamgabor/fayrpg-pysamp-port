from ..dialog_tree import DialogTree
from python.model.server import Player

from ._base import BaseNode
from python.utils.enums.dialog_style import DialogStyle

class ListNode(BaseNode):
    def __init__(self, node_name: str, content: str, button_1: str, button_2: str, title: str, has_tab: bool = False, has_header: bool = False, display: str = ""):
        super().__init__(node_name, content, button_1, button_2, title)

        self._has_header = has_header
        self.display = display
        
        if has_tab and has_header:
            self._dialog_style = DialogStyle.TABLIST_HEADERS
        elif has_tab:
            self._dialog_style = DialogStyle.TABLIST
        else:
            self._dialog_style = DialogStyle.LIST
    