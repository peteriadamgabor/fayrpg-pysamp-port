import re
from typing import Callable, Union

from pysamp.dialog import Dialog
from pysamp.player import Player
from python.utils.enums.dialog_style import DialogStyle
from ..helpers import paginate_or_trim_content

class BaseNode:
    def __init__(
        self,
        node_name: str,
        content: str,
        button_1: str,
        button_2: str,
        title: str,
    ):
        self.node_name: str = node_name
        self.title: str = title
        self.content: str = content
        self.button_1: str = button_1
        self.button_2: str = button_2

        self.display: str = ""
        self.max_list_length: int = 16
        self.jump_to_node: str = ""

        self.exit_on_button_2: bool = False
        self.back_to_root: bool = False
        self.close_in_end: bool = False
        self.back_after_input: bool = False
        self.stay_if_no_child: bool = False
        self.save_input: bool = False
        self.use_same_children: bool = False
        self.just_action: bool = False
        self.fixed_first_child: bool = False

        self.response_handler: Callable[
            [Player, int, int, str], Union[bool, None]
        ] = lambda player, response, list_item, input_text, *args, **kwargs: True
        self.response_handler_node_parameters: tuple[str, ...] = ()
        self.response_handler_parameters: tuple = ()

        self.close_handler: Callable[[Player], bool] = lambda player, *args: False
        self.close_handler_node_parameters: tuple = ()
        self.close_handler_parameters: tuple = ()

        self.content_creator: Callable[[Player], str] = lambda player, *args: ""
        self.content_creator_node_parameters: tuple = ()
        self.content_creator_parameters: tuple = ()

        self.guard: Callable[[Player], bool] = lambda player, *args: False
        self.guard_node_parameters: tuple = ()
        self.guard_parameters: tuple = ()
        self.guard_trigger_custom_handler: bool = True
        self.guard_run_before_show: bool = True
        self.guard_run_before_handler: bool = False

        self._dialog_style: DialogStyle = None
        self._dialog_tree: Union["DialogTree", None] = None
        self._children: list[Union["BaseNode", None]] = []
        self._parent: Union["BaseNode", None] = None
        self._active_page_number: int = 0
        self._selected_page_number: int = 0
        self._selected_list_item: int = 0

        self.dialogs: list[Dialog] = []
        self.dialogs_item_count: list[int] = []

        if self._parent is not None:
            self._dialog_tree = self._parent._dialog_tree

    def add_child(self, child: Union["BaseNode", list["BaseNode"], None]) -> None:
        """
        Add a child or a list of children to the node.
        """
        if isinstance(child, list):
            self._children.extend(child)
            for c in self._children:
                if c is not None:
                    c._parent = self
                    if self._parent is not None:
                        c._dialog_tree = self._parent._dialog_tree
        else:
            self._children.append(child)
            if child is not None:
                child._parent = self
                if self._parent is not None:
                    child._dialog_tree = self._parent._dialog_tree

    def set_tree(self, dialog_tree: "DialogTree"):
        self._dialog_tree = dialog_tree

    def set_dialog_style(self, dialog_style: DialogStyle):
        self._dialog_style = dialog_style

    def set_save_input(self, value: bool):
        self.save_input = value

    def get_children(self):
        return self._children

    def show(self, player: Player, page: int = 0) -> None:
        """
        Show the dialog for the given player.
        """

        self.dialogs.clear()
        self.dialogs_item_count.clear()

        if self.guard_run_before_show:
            if self._run_guard(player, -1, "NO PARAM"):
                return

        generated_content = self.get_generated_content(player)
        children_content = "\n".join([i.display for i in self._children])
        content = self.content + generated_content + children_content

        self._create_dialogs(content)
        self.dialogs[page].show(player)

    def get_generated_content(self, player: Player):
        return self.content_creator(player, *self._get_custom_args(self.content_creator_parameters, self.content_creator_node_parameters))

    def _run_guard(self, player: Player, list_item: int, input_text: str) -> bool:
        if self.guard(player, *self._get_custom_args(self.guard_parameters, self.guard_node_parameters)):
            if self._parent and not self.guard_trigger_custom_handler:
                self._parent._execute_custom_handler(player, list_item, input_text)
                self._parent.show(player)
                return True

            elif self.guard_trigger_custom_handler:
                self._execute_custom_handler(player, list_item, input_text)
                return True
        
        return False

    def _handler(self, player: Player, response: int, list_item: int, input_text: str) -> None:
        # If the player closes the dialog with button_2, ESC, or no button_2.
        if not bool(response):
            close_handler_result: bool = False

            if self.close_handler is not None:
                close_handler_result = self.close_handler(player, *self._get_custom_args(self.close_handler_parameters, self.close_handler_node_parameters))

            if close_handler_result:
                return

            if self.exit_on_button_2:
                return

            if self._parent is None:  # This is the root of the tree, close the dialog.
                return

            if self._process_jumping(player):
                return

            if self.back_to_root and self._dialog_tree:
                self._dialog_tree.root.show(player)
                return

            if self._parent._selected_page_number > 0:
                page = self._parent._selected_page_number
                self._parent.show(player, page)
                return

            self._parent.show(player)  # Just go back to the parent.
            return

        if self.guard_run_before_handler:
            if self._run_guard(player, list_item, input_text):
                return

        # Save the input_text from the dialog.
        if self.save_input and self._dialog_tree:
            self._dialog_tree.node_variables.setdefault(self.node_name, {})[f'input_value_0_-1'] = input_text

        if self._handle_paging(player, list_item, input_text):
            return

        self._selected_page_number = self._active_page_number
        self._selected_list_item = list_item

        if self._execute_custom_handler(player, list_item, input_text):
            self._deciding_next_node(player, list_item)
            return

        self._deciding_next_node(player, list_item)

    def _deciding_next_node(self, player: Player, list_item: int) -> None:
        if self._process_jumping(player):
            return

        if self.back_after_input and self._parent:
            self._parent.show(player)
            return

        if self.fixed_first_child and self._children:
            self._children[0].show(player)
            return

        if self.use_same_children and self._children:
            index = 1 if self.fixed_first_child and list_item > 1 else 0
            self._children[index].show(player)
            return

        if self.stay_if_no_child:
            self.show(player)
            return

        if self.back_to_root and self._dialog_tree:
            self._dialog_tree.root.show(player)
            return

        if not self.close_in_end and list_item <= len(self._children) - 1:
            item_index = sum(self.dialogs_item_count[:self._selected_page_number]) + list_item
            if item_index < len(self._children):
                self._children[item_index].show(player)
            else:
                if self._parent:
                    self._parent.show(player)
            return

        if not self.close_in_end and self._parent:
            self._parent.show(player)
            return

    def _execute_custom_handler(self, player: Player, list_item: int, input_text: str) -> bool:
        custom_args: list[str] = self._get_custom_args(
            self.response_handler_parameters,
            self.response_handler_node_parameters
        )

        result = self.response_handler(player, True, list_item, input_text, *custom_args)

        if not result and self.stay_if_no_child:
            self.show(player)
            return True

        if self.just_action:
            if self.back_after_input and self._parent:
                self._parent.show(player)
            return True

        if self.back_after_input and self._parent:
            self._parent.show(player)
            return True

        return False

    def _create_dialogs(self, content: str) -> None:
        for title, body in self._prepare_content(content):
            self.dialogs.append(Dialog.create(self._dialog_style, title, body, self.button_1, self.button_2, self._handler))
            shift: int = 0

            if ">>>" in body:
                shift += 1

            if "<<<" in body:
                shift += 1

            self.dialogs_item_count.append(body.count("\n") - shift)

    def _prepare_content(self, content: str) -> list[tuple[str, str]]:
        """
        Cleans the content from placeholders, inserts data in the right places,
        and fragments the content if necessary.
        """
        pattern = r'#(.*?)#'
        header = ""

        if content.startswith("\n"):
            content = content[1:]

        pages = paginate_or_trim_content(self._dialog_style, content, self.max_list_length)
        page_count = len(pages)

        shift = 1 if self._dialog_style == DialogStyle.TABLIST_HEADERS else 0

        if self._dialog_style == DialogStyle.TABLIST_HEADERS:
            header = pages[0].split('\n', 1)[0] + '\n'

        result = []
        for i, page in enumerate(pages):
            items = page.split('\n')
            items = self._process_items(items, pattern, i, shift)

            title = self._process_title(pattern, i, page_count)
            clean_content = '\n'.join(items)

            if self._dialog_style == DialogStyle.TABLIST_HEADERS and i != 0:
                clean_content = header + clean_content

            result.append((title, clean_content))

        return result

    def _process_items(self, items: list[str], pattern: str, page_index: int, shift: int) -> list[str]:
        for j, item in enumerate(items):
            matches = re.findall(pattern, item)
            for match in matches:
                _, value = self._extract_property(match, page_index, j - shift)
                item = item.replace(f'#{match}#', value)
            items[j] = item
        return items

    def _process_title(self, pattern: str, page_index: int, page_count: int) -> str:
        matches = re.findall(pattern, self.title)
        if matches:
            title = self.title
            for match in matches:
                node_name, prop = match.split(".")
                title = title.replace(f'#{match}#', self._get_node_value(node_name, prop))
        else:
            title = self.title
        return f"{title} ({page_index + 1} / {page_count})" if page_count > 1 else title

    def _extract_property(self, match_s: str, page_index: int, item_index: int) -> tuple[str, str]:
        if "->" in match_s:
            prop, value = match_s.split("->")
            self._set_property(prop, value, page_index, item_index)
            return prop, value

        if "~>" in match_s:
            prop, value = match_s.split("~>")
            self._set_property(prop, value, page_index, item_index)
            return prop, ""

        if "." in match_s:
            node_name, prop = match_s.split(".")
            value = self._get_node_value(node_name, prop)
            return prop, value

        return match_s, ""

    def _find_node_by_name(self, node_name: str) -> Union["BaseNode", None]:
        if self.node_name.lower() == node_name.lower():
            return self

        for node in self._children:
            if node:
                found_node = node._find_node_by_name(node_name)
                if found_node is not None:
                    return found_node

        return None

    def _handle_paging(self, player: Player, list_item: int, input_text: str) -> bool:
        page_move = 1 if ">>>" in input_text else -1 if "<<<" in input_text else 0

        if page_move != 0:
            self._active_page_number += page_move
            self.dialogs[self._active_page_number].show(player, self._active_page_number, list_item)
            return True

        return False

    def _process_jumping(self, player: Player) -> bool:
        if self.jump_to_node and self._dialog_tree:
            node = self._dialog_tree.root._find_node_by_name(self.jump_to_node)
            if node:
                node.show(player)
            elif self._parent:
                self._parent.show(player)
            return True
        return False

    def _get_custom_args(self, custom_parameters: tuple, custom_node_parameters: tuple):
        custom_args: list[str] = []

        custom_args.extend(custom_parameters)
        custom_args.extend(self._get_parameters(custom_node_parameters))

        return custom_args

    def _get_node_value(self, node_name: str, property_name: str) -> str:
        if not self._dialog_tree:
            return "N/A"

        node = self._dialog_tree.root._find_node_by_name(node_name)
        if not node and "input_value" not in property_name:
            return "N/A"

        if "input_value" in property_name:
            prop_key = "input_value_0_-1"
        else:
            prop_key = f"{property_name}_{node._selected_page_number}_{node._selected_list_item}"
        
        prop_dict = self._dialog_tree.node_variables.get(node_name, {})
        ret_value = prop_dict.get(prop_key, "N/A")

        return ret_value

    def _set_property(self, property_name: str, value: str, page: int, row: int) -> None:
        if not self._dialog_tree:
            return

        property_key = f"{property_name}_{page}_{row}"
        node_vars = self._dialog_tree.node_variables.setdefault(self.node_name, {})
        node_vars[property_key] = value

    def _get_parameters(self, raw_parameters):
        custom_args = []

        if not self._dialog_tree:
            return custom_args

        for raw_parameter in raw_parameters:
            node_name, prop = [part.replace("#", "") for part in raw_parameter.split(".")]
            node = self._dialog_tree.root._find_node_by_name(node_name)

            if node:
                if "input_value" in prop:
                    prop_key = "input_value_0_-1"
                else:
                    prop_key = f"{prop}_{node._selected_page_number}_{node._selected_list_item}"
                node_var = self._dialog_tree.node_variables.get(node_name, {})
            else:
                node_var =  {}
                prop_key = "N/A"

            node_prop = node_var.get(prop_key, "N/A")
            custom_args.append(node_prop)

        return custom_args


from ..dialog_tree import DialogTree # noqa