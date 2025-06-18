from sqlalchemy import select

from python.admin.functions import send_admin_action_multi_lang
from python.database.context_managger import transactional_session
from python.model.server import Player
from python.server.database import MAIN_SESSION
from python.utils.enums.colors import Color

from python.model.database import PlayerFine as PlayerFineDB


@Player.using_registry
def delete_fine_handler(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs):
    fine_id: int = int(args[0])
    target_player: Player = Player.get_registry_item(args[1])

    with transactional_session(MAIN_SESSION) as session:
        player_fine: PlayerFineDB = session.scalars(select(PlayerFineDB).where(PlayerFineDB.id == fine_id)).one()
        player_fine.is_payed = True

    send_admin_action_multi_lang(player, f"törötle az egyik tartozást {target_player.name}-nak/nek")
    target_player.send_system_message_multi_lang(Color.ORANGE, f"{player.role.name} {player.name} törötle az egyik tartozásod!")