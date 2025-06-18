import re
from dataclasses import dataclass, field
from typing import Callable, Union, Any

from pysamp.dialog import Dialog
from pysamp.player import Player
from python.utils.enums.dialog_style import DialogStyle


@dataclass
class DialogTreeNode:
    """
    :param node_name: Name of the node in the tree
    :param dialog_style: SAMP dialog_style
    :param title: SAMP Dialog title
    :param content: SAMP Dialog content
    :param button_1: SAMP Dialog button 1
    :param button_2: SAMP Dialog button 2
    :param max_list_length: Max list length if the dialog_style is a list.
                            If it is a message box it represent the max character number (x * 64), Default 16
    :param jump_to: The name of the node you want to jump to at the end of the process.
    :param exit_on_button_2: If it's True and you press the button 2 will close the dialog
    :param back_to_root: If it's True it will jump back to the root dialog and show it
    :param close_in_end: If it's True it will close the dialog if no more child element
    :param back_after_input: If it's True it will go back to the previous node.
                             This flag work for if the dialog an input or password style
    :param stay_if_none: If it's True and no children stay the current node
    :param save_input: If it's True it will save the input of the dialog
    :param use_same_children: If it's True it will use the same children
    :param just_action: If it's True it will close the dialog after the action
    :param custom_handler: This is the function that runs when you send the dialog with button 1
    :param custom_handler_node_parameters: These parameters came form other nodes.
    :param custom_handler_parameters: These parameters came form external variables
    :param custom_content_handler: This is a unique way of putting together the dialogue structure.
                                   For example: retrieve data from a database.
    :param custom_content_handler_node_parameters: These parameters came form other nodes.
    :param custom_content_handler_parameters:  These parameters came form external variables
    """

    node_name: str
    dialog_style: DialogStyle
    title: str
    content: str
    button_1: str
    button_2: str
    max_list_length: int = 16
    jump_to: str | None = None
    exit_on_button_2: bool = False
    back_to_root: bool = False
    close_in_end: bool = False
    back_after_input: bool = False
    stay_if_none: bool = False
    save_input: bool = False
    use_same_children: bool = False
    just_action: bool = False
    is_guarded_handler: bool = False
    fixed_first_chiled: bool = False
    custom_handler: Callable[[Player, int, int, str, ...], bool | None] | None = None
    custom_handler_node_parameters: tuple[str, ...] = None
    custom_handler_parameters: tuple[Any] = None
    custom_content_handler: Callable[..., str] | None = None
    custom_content_handler_node_parameters: tuple[str, ...] = None
    custom_content_handler_parameters: tuple[str, ...] = None
    guard: Callable[[Player, ...], bool] = lambda _: True
    guard_node_parameters: tuple[str, ...] = None
    guard_parameters: tuple[Any] = None

    __dialog_tree: Union["DialogTree", None] = None
    __children: list[Union["DialogTreeNode", None]] = field(default_factory=list)
    __parent: Union["DialogTreeNode", None] = None
    __active_page_number: int = 0
    __selected_page_number: int = 0
    __selected_list_item: int = 0

    dialogs: list[Dialog] = field(default_factory=list)

    def add_child(self, child: Union["DialogTreeNode", list["DialogTreeNode"], None]) -> None:
        """
        Add a child to the list. It is important to note that if it is a list type dialog,
        the order of the elements in the list must match the order of the elements in the list.
        :param child: The node.
        :return:
        """

        if isinstance(child, list):
            self.__children.extend(child)

            for i in self.__children:
                if i is not None:
                    i.__parent = self

                if self.__parent is not None:
                    self.__dialog_tree = self.__parent.__dialog_tree

        else:
            self.__children.append(child)

            if child is not None:
                child.__parent = self

                if self.__parent is not None:
                    self.__dialog_tree = self.__parent.__dialog_tree


    def apply_dialog_tree(self, tree) -> None:
        if self.__dialog_tree is None:
            self.__dialog_tree = tree
            for i in self.__children:
                if i is not None:
                    i.apply_dialog_tree(tree)

    def show(self, player: Player):
        """
        Show the dialog for the given player.

        :param player:
        :return:
        """

        if self.guard is not None:
            if not self.guard(player, *self.__get_guard_parameters()):
                if self.__parent.is_guarded_handler:
                    self.__parent.execute_custom_handler(player, "", "", "")
                self.__parent.show(player)

        if self.just_action:
            self.__handler(player, 1, -1, "-1")
            return

        content = self.content

        if self.custom_content_handler is not None:

            args: list[str] = self.__get_custom_content_handler_parameters()
            c_content = self.custom_content_handler(player, *args)

            if c_content == "":
                if self.__parent is None or self.back_to_root:
                    self.__dialog_tree.root.show(player)
                    return

                self.__parent.show(player)
                return

            content += c_content

        self.dialogs = self.__create_dialogs(content)

        self.dialogs[0].show(player)

    def __create_dialogs(self, content: str) -> list[Dialog]:

        return [Dialog.create(self.dialog_style, f_title, f_content, self.button_1, self.button_2, self.__handler)
                for f_title, f_content in self.__prepare_content(content)]

    def __prepare_content(self, content: str) -> tuple[str, str]:
        """
        Cleaning the content from the placeholders and inserting data in the right places
        and fragmenting the content if necessary.

        :param content: The dialog content
        :return: the title and the content
        """

        pattern = r'#(.*?)#'
        header = ""

        pages: list[str] = split_content_by_limit(self.dialog_style, content, self.max_list_length)
        page_count = len(pages)

        shift = 1 if self.dialog_style == DialogStyle.TABLIST_HEADERS else 0

        if self.dialog_style == DialogStyle.TABLIST_HEADERS:
            header = pages[0][:pages[0].find('\n') + 2]

        for i in range(page_count):
            items = pages[i].split('\n')
            item_count = len(items)

            for j in range(item_count):
                matches = re.findall(pattern, items[j])

                for match in matches:
                    if "->" in match:
                        prop = match.split("->")[0]
                        value = match.split("->")[1]

                        self.__set_property(prop, value, i, j - shift)
                        items[j] = items[j].replace(f'#{match}#', value)

                    elif "~>" in match:
                        prop = match.split("~>")[0]
                        value = match.split("~>")[1]

                        self.__set_property(prop, value, i, j - shift)
                        items[j] = items[j].replace(f'#{match}#', "")

                    elif "." in match:
                        node_name = match.split(".")[0].replace("#", "")
                        prop = match.split(".")[1].replace("#", "")

                        items[j] = items[j].replace(f'#{match}#', self.__get_node_value(node_name, prop))

            matches = re.findall(pattern, self.title)

            c_title = ""

            if matches:
                for match in matches:
                    node_name = match.split(".")[0]
                    prop = match.split(".")[1]

                    c_title = self.title.replace(f'#{match}#', self.__get_node_value(node_name, prop))
            else:
                c_title = self.title

            page_title = c_title if page_count == 1 else c_title + f" ({str(i + 1)}" + " / " + f"{page_count})"
            clean_content = '\n'.join(items)

            if self.dialog_style == DialogStyle.TABLIST_HEADERS and i != 0:
                clean_content = (header + clean_content)

            yield page_title, clean_content

    def __find_node_by_name(self, node_name: str) -> Union["DialogTreeNode", None]:

        if self.node_name.lower() == node_name.lower():
            return self

        for node in self.__children:
            if node.node_name.lower() == node_name.lower():
                return node

            else:
                r_node = node.__find_node_by_name(node_name)

                if r_node is not None:
                    return r_node

        return None

    def execute_custom_handler(self, player, response, list_item, input_text) -> Union[bool, None]:
        args: list[str] = self.__get_custom_handler_parameters()
        return self.custom_handler(player, response, list_item, input_text, *args)

    def __handler(self, player: Player, response: int, list_item: int, input_text: str):

        # if the player colse the dialog with the button_2 or ESC or no button_2.
        if not bool(response):
            if self.exit_on_button_2:
                return

            # In this case this is the root of the tree so you need close the dialog
            if self.__parent is None:
                return

            if self.__process_jumping(player):
                return

            # back to the tree root node.
            if self.back_to_root:
                self.__dialog_tree.root.show(player)
                return

            # just go back to the parent.
            self.__parent.show(player)
            return

        # save the input_text from the dialog.
        if self.save_input:
            self.__dialog_tree.node_variables[self.node_name] = {f'input_value_0_-1': input_text}

        if self.__handel_paging(player, list_item, input_text):
            return

        self.__selected_page_number: int = self.__active_page_number
        self.__selected_list_item: int = list_item

        if self.__execute_custom_handler(player, list_item, input_text):
            self.__deciding_next_node(player, list_item)
            return

        self.__deciding_next_node(player, list_item)

        return

    def __handel_paging(self, player: Player, list_item: int, input_text: str) -> bool:
        page_move = 1 if "<<<" in input_text else -1 if ">>>" in input_text else 0

        if page_move != 0:
            self.__active_page_number += page_move
            self.dialogs[self.__active_page_number].show(player, self.__active_page_number, list_item)
            return True

        return False

    def __execute_custom_handler(self, player: Player, list_item: int, input_text: str) -> bool:
        if self.custom_handler is not None:
            custom_handler_result = self.execute_custom_handler(player, True, list_item, input_text)

            if not custom_handler_result and self.stay_if_none:
                self.show(player)
                return True

            if self.just_action and self.back_after_input:
                self.__parent.show(player)
                return True

            if self.just_action:
                return True

            if self.back_after_input:
                self.__parent.show(player)
                return True

            return False

        return False

    def __deciding_next_node(self, player: Player, list_item: int):

        if self.__process_jumping(player):
            return

        if self.back_after_input:
            self.__parent.show(player)
            return

        if self.fixed_first_chiled and list_item == 0:
            self.__children[0].show(player)
            return

        if self.use_same_children and self.fixed_first_chiled and list_item > 1:
            self.__children[1].show(player)
            return

        if self.use_same_children and not self.fixed_first_chiled:
            self.__children[0].show(player)
            return

        if self.stay_if_none:
            self.show(player)
            return

        if self.back_to_root:
            self.__dialog_tree.root.show(player)
            return

        if self.close_in_end:
            return

        if list_item > len(self.__children) - 1:
            self.__parent.show(player)
            return

        self.__children[list_item].show(player)

    def __process_jumping(self, player: Player) -> bool:
        # The jump_to is contins a node name. Defult None.
        if self.jump_to is not None:

            # search the node in the tree.
            node = self.__dialog_tree.root.__find_node_by_name(self.jump_to)

            # if the node is founded we will show the player.
            if node is not None:
                node.show(player)
                return True

            # other hand we go back to tha parent.
            else:
                self.__parent.show(player)
                return True
        return False

    def __get_custom_content_handler_parameters(self):
        args: list[str] = []

        if self.custom_content_handler_parameters is not None:
            args.extend(self.custom_content_handler_parameters)

        if self.custom_content_handler_node_parameters is not None:
            args.extend(self.__get_parameters(self.custom_content_handler_node_parameters))

        return args

    def __get_custom_handler_parameters(self):
        args: list[str] = []

        if self.custom_handler_parameters is not None:
            args.extend(self.custom_handler_parameters)

        if self.custom_handler_node_parameters is not None:
            args.extend(self.__get_parameters(self.custom_handler_node_parameters))

        return args

    def __get_guard_parameters(self):
        args: list[str] = []

        if self.guard_parameters is not None:
            args.extend(self.custom_handler_parameters)

        if self.guard_node_parameters is not None:
            args.extend(self.__get_parameters(self.guard_node_parameters))

        return args

    def __get_node_value(self, node_name: str, property_name: str) -> str:
        node = self.__dialog_tree.root.__find_node_by_name(node_name)
        prop_key: str = property_name + f"_{str(node.__selected_page_number)}_{str(node.__selected_list_item)}"

        prop_dict = self.__dialog_tree.node_variables.get(node_name)

        if prop_dict is not None:

            prop_val = prop_dict.get(prop_key)

            if prop_val is not None:
                return prop_val

        return "Nincs"

    def __set_property(self, property_name: str, value: str, page: int, row: int) -> None:
        property_key: str = property_name + f"_{str(page)}_{str(row)}"

        if self.node_name in self.__dialog_tree.node_variables:
            self.__dialog_tree.node_variables[self.node_name][property_key] = value

        else:
            self.__dialog_tree.node_variables[self.node_name] = {property_key: value}

    def __get_parameters(self, raw_parameters):

        args = []

        for raw_parameter in raw_parameters:
            node_name = raw_parameter.split(".")[0].replace("#", "")
            prop = raw_parameter.split(".")[1].replace("#", "")

            node = self.__dialog_tree.root.__find_node_by_name(node_name)

            if node is not None:
                prop_key: str = prop + f"_{str(node.__selected_page_number)}_{str(node.__selected_list_item)}"
                node_var = self.__dialog_tree.node_variables.get(node_name)

                if node_var is not None:
                    node_prop = node_var.get(prop_key)
                    args.append(node_prop)

        return args


# region helpers

def find_all_char(text: str, ch: str):
    for i, ltr in enumerate(text):
        if ltr == ch:
            yield i


def content_splitter(content: str, max_item) -> list[str]:
    index_list: list[int] = list(find_all_char(content, "\n"))[max_item - 1::max_item]
    start: int = 0
    acc: list[str] = []

    for i in index_list:
        chunk = content[start:i]
        start = i + 1
        acc.append(chunk)

    acc.append(content[start:])

    return acc


def split_content_by_limit(dialog_style, content: str, max_list_length: int) -> list[str]:
    if dialog_style not in [DialogStyle.MSGBOX, DialogStyle.LIST, DialogStyle.TABLIST, DialogStyle.TABLIST_HEADERS]:
        return [content]

    if len(content) >= max_list_length * 64:

        if dialog_style == DialogStyle.MSGBOX:
            return [content[:max_list_length * 64]]

        splitup = content_splitter(content, max_list_length)
        pages = len(splitup)

        for i in range(pages):

            if splitup[i][-1:] != '\n':
                splitup[i] += '\n'
            elif splitup[i][-1:] == '\n':
                splitup[i] += '\n'

            if i == 0:
                splitup[i] += f">>>"
            elif i < pages - 1:
                splitup[i] += ">>>\n<<<"
            elif i == pages - 1:
                splitup[i] += "<<<"

        return splitup
    return [content]

# endregion helpers