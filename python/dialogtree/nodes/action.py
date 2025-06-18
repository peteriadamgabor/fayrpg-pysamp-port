from typing import Union

from pysamp.player import Player

from ._base import BaseNode
from python.model.server import Player


class ActionNode(BaseNode):
    def __init__(self, node_name: str, display: str = ""):
        super().__init__(node_name, "None", "None", "None", "None")
        self.display = display

    def add_child(self, child: Union["BaseNode", None]) -> None: # type: ignore
        raise RuntimeError("You can't add a child for an action Node!")

    def show(self, player: Player) -> None: # type: ignore

        if self.guard_run_before_show:
            if self._run_guard(player, -1, "NO PARAM"):
                return

        super()._execute_custom_handler(player, -1, "")

        if self.jump_to_node:
            super()._process_jumping(player)
            return

        if self.back_to_root:
            self._dialog_tree.root.show(player)
            return

        if self.close_in_end:
            return

        if self._parent:
            self._parent.show(player)
