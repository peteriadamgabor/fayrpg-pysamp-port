import re
import random

from python.model.database import bank_account
from python.model.server import Player
from python.server.database import MAIN_SESSION
from python.utils.enums.colors import Color
from python.utils.helper.python import try_parse_float, try_parse_int


@Player.using_registry
def deposit_handler(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs) -> bool:
    amount = try_parse_float(input_text)

    if amount is None:
        player.send_client_message(Color.RED, "(( Számmal kell megadni! ))")
        return False

    if amount <= 0:
        player.send_client_message(Color.RED, "(( Hibás pénzegység! ))")
        return False

    if player.money < amount:
        player.send_client_message(Color.RED, "(( Nincs nálad ennyi pénzed! ))")
        return False

    player.money -= amount

    bank_account_id = try_parse_int(args[0])

    if bank_account_id is not None:
        with MAIN_SESSION() as session:
            bank_acc: bank_account = session.query(bank_account).filter(bank_account.id == bank_account_id).first()
            bank_acc.balance += amount
            session.commit()

    else:
        with MAIN_SESSION() as session:
            bank_acc: bank_account = session.query(bank_account).filter(bank_account.number == args[0]).first()
            bank_acc.balance += amount
            session.commit()

    player.send_client_message(Color.GREEN, "(( A tranzakció sikersen lezárul! ))")

    return True


@Player.using_registry
def withdrawal_handler(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs) -> bool:
    amount = try_parse_float(input_text)

    if amount is None:
        player.send_client_message(Color.RED, "(( Számmal kell megadni! ))")
        return False

    bank_account_id = try_parse_int(args[0])

    with MAIN_SESSION() as session:
        if bank_account_id is not None:
            bank_acc: bank_account = session.query(bank_account).filter(bank_account.id == bank_account_id).first()
        else:
            bank_acc: bank_account = session.query(bank_account).filter(bank_account.number == args[0]).first()

        if bank_acc.balance < amount:
            player.send_client_message(Color.RED, "(( Nincs ennyi pénz a számlán! ))")
            return False

        else:
            bank_acc.balance -= amount
            player.money += amount
            session.commit()

    player.send_client_message(Color.GREEN, "(( A tranzakció sikersen lezárul! ))")
    return True


@Player.using_registry
def change_password_bank_account(player: Player, response: int, list_item: int, input_text: str, *args) -> bool:
    regex = r"^\d{4,6}$"

    matches = re.findall(regex, input_text, re.MULTILINE)

    if len(matches) == 0:
        player.send_client_message(Color.RED, "(( 4 és 6 karakter közt kell lennie a jelszónak! ))")
        return False

    bank_account_id = try_parse_int(args[0])

    with MAIN_SESSION() as session:
        if bank_account_id is not None:
            bank_acc: bank_account = session.query(bank_account).filter(bank_account.id == bank_account_id).first()
        else:
            bank_acc: bank_account = session.query(bank_account).filter(bank_account.number == args[0]).first()

        bank_acc.password = input_text
        session.commit()

    player.send_client_message(Color.GREEN, "(( A jelszó sikeresen megváltoztaca! ))")

    return True


@Player.using_registry
def deposit_bank_validator(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs) -> bool:
    with MAIN_SESSION() as session:
        bank_acc: bank_account = session.query(bank_account).filter(bank_account.number == args[0]).first()

        if bank_acc is None:
            player.send_client_message(Color.RED, f"(( Ismertelen számlaszám! {args[0]} ))")
            return False

        return True


@Player.using_registry
def bank_info_content_handler(player: Player, *args) -> str:
    bank_account_id = try_parse_int(args[0])

    with MAIN_SESSION() as session:
        if bank_account_id is not None:
            bank_acc: bank_account = session.query(bank_account).filter(bank_account.id == bank_account_id).first()
        else:
            bank_acc: bank_account = session.query(bank_account).filter(bank_account.number == args[0]).first()

    return f"Számlaszám: {bank_acc.number}\nEgyenleg: {bank_acc.balance}"


@Player.using_registry
def list_player_bank_accounts(player: Player, *args) -> str:
    with MAIN_SESSION() as session:
        bank_accounts: list[bank_account] = session.query(bank_account).filter(bank_account.owner_id == player.dbid).all()

        if len(bank_accounts) == 0:
            player.send_client_message(Color.RED, "(( Nincs számlád! ))")
            return ""

        return "\n".join([f"{i.number}#id~>{i.id}#" for i in bank_accounts])


@Player.using_registry
def create_new_bank_account(player: Player, response: int, list_item: int, input_text: str, *args) -> None:
    regex = r"^\d{4,6}$"

    matches = re.findall(regex, input_text, re.MULTILINE)

    if len(matches) == 0:
        player.send_client_message(Color.RED, "(( 4 és 6 karakter közt kell lennie a jelszónak! ))")
        return

    with MAIN_SESSION() as session:
        number: str = f"117{random.randint(1_000, 9_999)}-{random.randint(1_000_000, 9_999_999)}"
        password: str = input_text
        balance: float = 0.0
        owner_id: int = player.dbid
        business_id: int | None = None
        fraction_id: int | None = None
        is_default: bool = False

        bank_acc: bank_account = bank_account(number=number, password=password, balance=balance,
                                            owner_id=owner_id, business_id=business_id, fraction_id=fraction_id,
                                            is_default=is_default)

        session.add(bank_acc)
        session.commit()

        player.send_client_message(Color.GREEN, f"((Bankszámla sikeresen létrehozva! Számlaszám: {number}))")
        return


@Player.using_registry
def check_bank_password(player: Player, response: int, list_item: int, input_text: str, *args, **kwargs) -> bool:
    if args:
        bank_acc_id = int(args[0])
        with (MAIN_SESSION() as session):
            bank_accounts: bank_account = session.query(bank_account).filter(bank_account.id == bank_acc_id,
                                                                           bank_account.password == input_text
                                                                           ).one_or_none()

            return bank_accounts is not None
