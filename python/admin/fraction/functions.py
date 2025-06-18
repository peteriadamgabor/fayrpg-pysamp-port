from sqlalchemy import asc, select

from python.model.database import division, fraction, player, player_parameter, rank
from python.model.server import Player
from python.server.database import MAIN_SESSION
from python.utils.enums.colors import Color
from ..functions import send_admin_action


def list_fractions(player: Player) -> str:
    with MAIN_SESSION() as session:
        fractions: list[fraction] = session.query(fraction).all()
        return "\n".join([f"#id~>{fraction.id}##name->{fraction.name}#" for fraction in fractions])


def list_fraction_parameter(player: Player, fraction_id: int) -> str:
    with MAIN_SESSION() as session:
        fid = int(fraction_id)

        fraction: fraction = session.query(fraction).filter(fraction.id == fid).one()
        divisions: list[division] = session.query(division).filter(division.fraction_id == fid).all()
        ranks: list[rank] = session.query(rank).filter(rank.fraction_id == fid).all()
        players: list[player] = session.query(player).filter(player.fraction_id == fid).all()

        return (f"Név:\t{fraction.name}\n"
                f"Rövidítés:\t{fraction.acronym}\n"
                f"Alosztályok:\t{len(divisions)} db\n"
                f"Rangok:\t{len(ranks)} db\n"
                f"Tagok:\t{len(players)} db")


def list_fraction_players(player: Player, fraction_id: int) -> str:
    with MAIN_SESSION() as session:
        fid = int(fraction_id)

        players: list[player] = session.query(player).filter(player.fraction_id == fid).all()

        return "\n".join([f"#id~>{player.id}##name->{player.name.replace("_", " ")}#\tValami rang\t"
                          f"{"{{33AA33}}Online" if player.id is not None else "{{AA3333}}Offline"}" for player
                          in players])


def list_player_data(player: Player, player_id: int) -> str:
    with MAIN_SESSION() as session:
        pid = int(player_id)

        player: player = session.query(player).filter(player.id == pid).one()

        player_param: player_parameter = session.query(player_parameter).filter(
            player_parameter.player_id == player.id).one()

        return (f"Rang:\t{player.rank.name}\n"
                f"Alosztály:\t{player.division.name if player.division else "Nincs"}\n"
                f"Vezető:\t{"Igen" if player_param.is_leader else "Nem"}\n"
                f"Alosztály Vezető:\t{"Igen" if player_param.is_division_leader else "Nem"}\n"
                f"Kirúgás\t{""}\n"
                )


def list_ranks_for_promot(player: Player, player_id: int) -> str:
    with MAIN_SESSION() as session:
        pid = int(player_id)

        player: player = session.query(player).filter(player.id == pid).one()
        stmt = None

        if player.division is not None:
            stmt = (select(rank).where(
                (rank.fraction_id == player.fraction_id) & (rank.division_id == player.division_id) & (
                        rank.id != player.rank_id)).order_by(asc(rank.order)))
            ranks: list[rank] = session.scalars(stmt)

            if len(ranks) == 0:
                stmt = (select(rank).where((rank.fraction_id == player.fraction_id) & (rank.division_id == None) & (
                        rank.id != player.rank_id)).order_by(asc(rank.order)))
                ranks: list[rank] = session.scalars(stmt)

        else:
            stmt = (select(rank).where((rank.fraction_id == player.fraction_id) & (rank.division_id == None) & (
                    rank.id != player.rank_id)).order_by(asc(rank.order)))
            ranks: list[rank] = session.scalars(stmt)

        return "\n".join([f"#id~>{rank.id}#{rank.name}" for rank in ranks])


@Player.using_registry
def promote_player(player: Player, response, list_item, input_text, *args) -> None:
    with MAIN_SESSION() as session:
        pid = int(args[0])
        rankid = int(args[1])

        target_player: player = session.query(player).filter(player.id == pid).one()
        rank: rank = session.query(rank).filter(rank.id == rankid).one()

        if target_player.in_game_id is not None:
            if rank.order > target_player.rank.order:
                Player(target_player.in_game_id).send_system_message(Color.ORANGE,
                                                                     f"{player.role.name} {player.name} előléptetett {rank.name}-nak/nek")
            else:
                Player(target_player.in_game_id).send_system_message(Color.ORANGE,
                                                                     f"{player.role.name} {player.name} lefokozott {rank.name}-ra/re")

        player.send_system_message(Color.GREEN, f"Sikeresen módosítottad a rangot!")
        target_player.rank_id = rankid
        session.commit()
    return


@Player.using_registry
def change_player_deivison(player: Player, response, list_item, input_text, *args) -> None:
    with MAIN_SESSION() as session:
        pid = int(args[0])
        divid = int(args[1])

        target_player: player = session.scalars(select(player).where(player.id == pid)).first()
        division: division = session.scalars(select(division).where(division.id == divid)).first()
        Player(target_player.in_game_id).send_system_message(Color.ORANGE, f"{player.role.name} {player.name} "
                                                                           f"áthelyezett a(z) {division.name}"
                                                                           f" alosztályba!")

        player.send_system_message(Color.GREEN, f"Sikeresen áthelyezted a játékost!")
        target_player.division_id = divid
        session.commit()
    return


def list_possible_divisions(player: Player, player_id: int) -> str:
    with MAIN_SESSION() as session:
        pid = int(player_id)

        player: player = session.query(player).filter(player.id == pid).one()

        stmt = (select(division).where(
            (division.fraction_id == player.fraction_id) & (division.fraction_id != player.division_id)))
        divisions: list[division] = session.scalars(stmt)
        return "\n".join([f"#id~>{division.id}#{division.name}" for division in divisions])


def list_fraction_ranks(player: Player, fraction_id: int) -> str:
    with MAIN_SESSION() as session:
        fid = int(fraction_id)

        ranks: list[rank] = session.query(rank).filter(rank.fraction_id == fid).order_by(asc(rank.order)).all()

        return "\n".join(
            [f"{rank.order} - {rank.division.name if rank.division else ""} {rank.name}" for rank in ranks])


@Player.using_registry
def change_fraction_name(player: Player, response, list_item, input_text, fraction_id) -> bool:
    with MAIN_SESSION() as session:
        fid = int(fraction_id)
        fraction: fraction = session.query(fraction).filter(fraction.id == fid).one()

        player.send_system_message(Color.GREEN, f"Sikeresen megváltoztattad a {fraction.name}-et {input_text}-re")
        send_admin_action(player, f"Megváltoztatta a(z) {fraction.name} frakció nevét {input_text}-re")

        fraction.name = input_text
        session.commit()

        return True


@Player.using_registry
def change_fraction_acronym(player: Player, response, list_item, input_text, *args) -> bool:
    with MAIN_SESSION() as session:
        fid = int(args[0])
        fraction: fraction = session.query(fraction).filter(fraction.id == fid).one()

        player.send_system_message(Color.GREEN, f"Sikeresen megváltoztattad a {fraction.acronym}-et {input_text}-re")
        send_admin_action(player, f"Megváltoztatta a(z) {fraction.acronym} frakció rövidítését {input_text}-re")

        fraction.acronym = input_text
        session.commit()

        return True


@Player.using_registry
def save_fraction_new_rank(player: Player, response, list_item, input_text, *args) -> bool:
    with MAIN_SESSION() as session:

        order = int(args[0])
        name = args[1]
        fraction_id = int(args[2])

        new_rank: rank = rank(order=order, name=name, fraction_id=fraction_id)
        fraction: fraction = session.query(fraction).filter(fraction.id == fraction_id).one()

        session.add(new_rank)

        player.send_system_message(Color.GREEN, f"Sikeresen létrehoztad az új rangot {name} a {fraction.name}-hez")
        send_admin_action(player, f"Új rangot hozott létre {name} a {fraction.name}-hez")

        session.commit()

        return True
