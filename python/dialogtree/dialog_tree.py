from pysamp.player import Player

class DialogTree:
    def __init__(self, root = None):
        self.root = root
        self.node_variables: dict[str, dict[str, str]] = {}

        if root is not None:
            self.root._dialog_tree = self

    def show_root_dialog(self, player: Player) -> None:
        self._set_all_node_dialog_tree(self.root)
        self.root.show(player)

    def _set_all_node_dialog_tree(self, node):
        node.set_tree(self)

        for i in node._children:
            self._set_all_node_dialog_tree(i)

    def add_root(self, root) -> None:
        self.root = root
        root._dialog_tree = self

