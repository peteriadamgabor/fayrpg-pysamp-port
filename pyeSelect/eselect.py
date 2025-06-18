from dataclasses import dataclass, field
from typing import Callable, List, Any

from samp import INVALID_TEXT_DRAW

import pysamp
from pysamp import on_gamemode_init
from pysamp.player import Player
from pysamp.playertextdraw import PlayerTextDraw
from pysamp.textdraw import TextDraw

ITEMS_PER_PAGE = 18


class StaticGraphics:
    """Contains static graphics elements (background, etc.) textdraws."""

    def __init__(self):
        self.background = TextDraw.create(
            531.333374,
            140.877777,
            '_'
        )
        self.background.background_color(0)
        self.background.alignment(1)
        self.background.font(0)
        self.background.letter_size(0.0, 22.912965)
        self.background.color(0)
        self.background.set_outline(0)
        self.background.set_proportional(True)
        self.background.set_shadow(1)
        self.background.use_box(True)
        self.background.box_color(0x000000DD)
        self.background.text_size(121.333328, 0.000000)
        self.background.set_selectable(False)

        self.right_arrow = TextDraw.create(
            521.333374,
            339.318542,
            'LD_BEAT:right'
        )
        self.right_arrow.letter_size(0.000000, 0.000000)
        self.right_arrow.text_size(5.999938, 7.051818)
        self.right_arrow.alignment(1)
        self.right_arrow.color(0xC0C0C0FF)
        self.right_arrow.set_shadow(0)
        self.right_arrow.set_outline(0)
        self.right_arrow.font(4)
        self.right_arrow.set_selectable(True)

        self.left_arrow = TextDraw.create(
            507.000305,
            339.074066,
            'LD_BEAT:left'
        )

        self.left_arrow.letter_size(0.000000, 0.000000)
        self.left_arrow.text_size(5.999938, 7.051818)
        self.left_arrow.alignment(1)
        self.left_arrow.color(0xC0C0C0FF)
        self.left_arrow.set_shadow(0)
        self.left_arrow.set_outline(0)
        self.left_arrow.font(4)
        self.left_arrow.set_selectable(True)

        self.top_banner = TextDraw.create(
            531.000244,
            155.811111,
            'TopBanner'
        )
        self.top_banner.letter_size(0.000000, -0.447120)
        self.top_banner.text_size(121.333328, 0.000000)
        self.top_banner.alignment(1)
        self.top_banner.color(0)
        self.top_banner.use_box(True)
        self.top_banner.box_color(0x808080FF)
        self.top_banner.set_shadow(0)
        self.top_banner.set_outline(0)
        self.top_banner.font(0)

        self.bottom_banner = TextDraw.create(
            531.333618,
            338.500305,
            'BottomBanner'
        )

        self.bottom_banner.letter_size(0.000000, -0.447120)
        self.bottom_banner.text_size(121.333328, 0.000000)
        self.bottom_banner.alignment(1)
        self.bottom_banner.color(0)
        self.bottom_banner.use_box(True)
        self.bottom_banner.box_color(0x808080FF)
        self.bottom_banner.set_shadow(0)
        self.bottom_banner.set_outline(0)
        self.bottom_banner.font(0)

        self.close_button = TextDraw.create(
            490.666809,
            337.829711,
            'CLOSE'
        )
        self.close_button.letter_size(0.128333, 0.957036)
        self.close_button.text_size(10.5021, 10.0187)
        self.close_button.alignment(2)
        self.close_button.color(0xC0C0C0FF)
        self.close_button.set_shadow(0)
        self.close_button.set_outline(00)
        self.close_button.background_color(0x00000033)
        self.close_button.font(2)
        self.close_button.set_proportional(True)
        self.close_button.set_selectable(True)

    def show(self, player: Player):
        self.right_arrow.show_for_player(player)
        self.left_arrow.show_for_player(player)
        self.background.show_for_player(player)
        self.top_banner.show_for_player(player)
        self.bottom_banner.show_for_player(player)
        self.close_button.show_for_player(player)

    def hide(self, player: Player):
        self.right_arrow.hide_for_player(player)
        self.left_arrow.hide_for_player(player)
        self.background.hide_for_player(player)
        self.top_banner.hide_for_player(player)
        self.bottom_banner.hide_for_player(player)
        self.close_button.hide_for_player(player)


@dataclass
class MenuItem:
    """A menu item containing a 3D model and a text label."""
    model_id: int
    text: str = ''
    rot_x: float = 0.
    rot_y: float = 0.
    rot_z: float = 0.
    zoom: float = 1.
    color_1: int = 1
    color_2: int = 0


@dataclass
class Menu:
    """A menu that has a title and a list of menu items."""
    title: str
    items: List[MenuItem] = field(default_factory=list)
    on_select: Callable[[Player, MenuItem], None] = lambda player, item: None
    on_cancel: Callable[[Player], None] = lambda player: None
    additional_data: tuple[Any, ...] = field(default_factory=tuple)

    def add(self, item):
        if item in self.items:
            raise ValueError(
                f'Adding the same menu item to the same menu twice: {item:r}'
            )

        self.items.append(item)

    def remove(self, item):
        if item not in self.items:
            raise ValueError(
                f'Removing menu item not present in menu: {item:r}'
            )

        self.items.remove(item)

    def show(self, player: Player):
        global _player_menus

        if not player.is_connected():
            return

        if _player_menus.get(player.id):
            _player_menus[player.id].hide()

        _player_menus[player.id] = player_menu = PlayerMenu(self, player)
        player_menu.show()


@dataclass
class PlayerMenu:
    """A menu that is being shown to a player. Handles paging, etc."""
    menu: Menu
    player: Player

    _show_time: int = 0
    _current_page: int = 0
    _total_pages: int = 0

    _paging_text: PlayerTextDraw | None = None
    _header_text: PlayerTextDraw | None = None
    _item_models: dict[int, PlayerTextDraw] = field(default_factory=dict)
    _item_texts: dict[int, PlayerTextDraw] = field(default_factory=dict)

    def __post_init__(self):
        # eg. 18 items in list, 18 items per page, should be one.
        # Same for 17, but not for 19.
        # This will also be zero if there's no items.
        self._total_pages = (len(self.menu.items) - 1) // ITEMS_PER_PAGE + 1

    def show(self):
        if not _static_graphics:
            raise RuntimeError(
                f"{__name__} module isn't initialized. "
                f"Did you forget to pyload('{__name__.partition('.')[2]}')?"
            )

        self._show_time = pysamp.get_tick_count()
        self._destroy_player_textdraws()
        self._create_player_textdraws()

        for index, item in enumerate(self.menu.items[:ITEMS_PER_PAGE]):
            self._show_item_at_index(item, index)

        player = self.player

        self._paging_text.set_string(f'1/{self._total_pages}')
        self._header_text.set_string(self.menu.title)

        self._paging_text.show()
        self._header_text.show()

        _static_graphics.show(player)
        pysamp.select_text_draw(player.id, 0xFFFFFFFF)

    def hide(self):
        global _player_menus
        self._destroy_player_textdraws()
        _static_graphics.hide(self.player)
        pysamp.cancel_select_text_draw(self.player.id)
        del _player_menus[self.player.id]

    def set_page(self, page):
        if not (0 <= page < self._total_pages):
            return

        for (_, item_model), (_, item_text) in zip(self._item_models.items(), self._item_texts.items()):
            pysamp.player_text_draw_hide(self.player.id, item_model.id)
            pysamp.player_text_draw_hide(self.player.id, item_text.id)

        start_index = ITEMS_PER_PAGE * page

        for index, item in enumerate(
                self.menu.items[start_index:start_index + ITEMS_PER_PAGE]
        ):
            self._show_item_at_index(item, index)

        self._current_page = page
        self._paging_text.set_string(f'{page + 1}/{self._total_pages}')

    def next_page(self):
        if self._current_page >= self._total_pages - 1:
            return

        self.set_page(self._current_page + 1)

    def previous_page(self):
        if self._current_page <= 0:
            return

        self.set_page(self._current_page - 1)

    def showed_at_least(self, ticks):
        return pysamp.get_tick_count() - self._show_time >= ticks

    def get_clicked_item(self, playertextid):
        val_list = list(self._item_models.values())
        index: int | None = None

        for i in range(len(val_list)):
            if val_list[i].id == playertextid:
                index = i
                break

        if index is None:
            return None

        return self.menu.items[self._current_page * ITEMS_PER_PAGE + index]

    def on_select(self, item):
        self.menu.on_select(self.player, item, *self.menu.additional_data)

    def on_cancel(self):
        self.menu.on_cancel(self.player)

    def _create_player_textdraws(self):
        player: Player = self.player

        self._paging_text = PlayerTextDraw.create(
            player,
            495.333251,
            139.792648,
            '0/1'
        )

        self._paging_text.letter_size(0.190666, 1.110518)
        self._paging_text.alignment(3)
        self._paging_text.color(0xC0C0C0FF)
        self._paging_text.set_shadow(0)
        self._paging_text.set_outline(1)
        self._paging_text.background_color(0x00000033)
        self._paging_text.font(2)
        self._paging_text.set_proportional(True)

        self._header_text = PlayerTextDraw.create(
            player,
            128.333312,
            139.377761,
            'header'
        )

        self._paging_text.letter_size(0.315000, 1.247407)
        self._paging_text.alignment(1)
        self._paging_text.color(0xC0C0C0FF)
        self._paging_text.set_shadow(0)
        self._paging_text.set_outline(1)
        self._paging_text.background_color(0x00000033)
        self._paging_text.font(2)
        self._paging_text.set_proportional(True)

        item_models, item_texts = self._item_models, self._item_texts
        origin = (140., 162.)

        for index, item in enumerate(self.menu.items):
            if index >= ITEMS_PER_PAGE:
                break

            # Hard-coded because that's how it was
            current_col = index % 6
            current_line = index // 6
            current_coords = (
                origin[0] + 62 * current_col,
                origin[1] + 55 * current_line,
            )

            item_model = PlayerTextDraw.create(
                player,
                current_coords[0],
                current_coords[1],
                '_'
            )
            item_models[index] = item_model

            item_model.background_color(0xD3D3D344)
            item_model.font(5)
            item_model.letter_size(1.430000, 5.700000)
            item_model.color(0xC0C0C0FF)
            item_model.set_outline(1)
            item_model.set_proportional(True)
            item_model.use_box(True)
            item_model.box_color(0)
            item_model.text_size(61.000000, 54.000000)
            item_model.set_selectable(True)

            item_text = PlayerTextDraw.create(
                player,
                current_coords[0] + 31,
                current_coords[1], '_'
            )
            item_texts[index] = item_text

            item_text.font(2)
            item_text.letter_size(0.199999, 0.6)
            item_text.alignment(2)
            item_text.set_outline(0)
            item_text.set_proportional(True)
            item_text.text_size(0.0, 62.0)
            item_text.set_shadow(0)
            item_text.color(0xD3D3D3AA)

    def _destroy_player_textdraws(self):

        if self._paging_text and self._header_text:
            pysamp.player_text_draw_destroy(self.player.id, self._paging_text.id)
            pysamp.player_text_draw_destroy(self.player.id, self._header_text.id)

        self._paging_text = None
        self._header_text = None

        for (_, item_model), (_, item_text) in zip(self._item_models.items(), self._item_texts.items()):
            pysamp.player_text_draw_destroy(self.player.id, item_model.id)
            pysamp.player_text_draw_destroy(self.player.id, item_text.id)

        self._item_models = {}
        self._item_texts = {}

    def _show_item_at_index(self, item, index):
        item_model = self._item_models.get(index, None)

        if not item_model:
            return

        pysamp.player_text_draw_set_preview_model(self.player.id, item_model.id, item.model_id)

        item_model.set_preview_rotation(item.rot_x,
                                        item.rot_y,
                                        item.rot_z,
                                        item.zoom)

        if item.model_id >= 400 or item.model_id <= 611:
            item_model.set_preview_vehicle_color(item.color_1, item.color_2)

        pysamp.player_text_draw_show(self.player.id, item_model.id)

        if item.text:
            item_text = self._item_texts[index]
            item_text.set_string(item.text)
            pysamp.player_text_draw_show(self.player.id, item_text.id)


_static_graphics: StaticGraphics | None = None
_player_menus = {}


@on_gamemode_init
def server_init():
    global _static_graphics
    _static_graphics = StaticGraphics()


@Player.on_click_textdraw
def on_click_text_draw(player: Player, clicked_text_draw: TextDraw):

    global _static_graphics, _player_menus

    if not _player_menus.get(player.id):
        return

    player_menu = _player_menus[player.id]

    # Handle on_select showing another Menu
    if not player_menu.showed_at_least(600):
        return

    if clicked_text_draw.id in (INVALID_TEXT_DRAW, _static_graphics.close_button.id):
        player_menu.on_cancel()
        player_menu.hide()

    elif clicked_text_draw.id == _static_graphics.right_arrow.id:
        player_menu.next_page()

    elif clicked_text_draw.id == _static_graphics.left_arrow.id:
        player_menu.previous_page()


@Player.on_click_playertextdraw
def on_click_player_text_draw(player: Player, player_text_draw: PlayerTextDraw):
    global _static_graphics, _player_menus

    if not _player_menus.get(player.id):
        return

    player_menu = _player_menus[player.id]

    # Handle on_select showing another Menu
    if not player_menu.showed_at_least(600):
        return

    item = player_menu.get_clicked_item(player_text_draw.id)

    if not item:
        return

    player_menu.hide()
    player_menu.on_select(item)
