import atexit

from sqlalchemy import select
from python.database.context_managger import transactional_session
from python.server.database import UTIL_SESSION
from python.model.server import Labale
from python.model.database import Label as LabaleDB
from python.utils.enums.colors import Color

def init_module():
    print(f"Module {__name__} is being initialized.")
    load_labels()


def load_labels():
    with transactional_session(UTIL_SESSION) as session:
        labels: list[LabaleDB] = list(session.scalars(select(LabaleDB)).all())

        for label in labels:
            labelsrv = Labale.create(label.text, Color[label.color], label.x, label.y, label.z, label.dd, world_id=label.vw, interior_id=label.interior)
            labelsrv.init_label(label.id, label.text, label.color, label.x, label.y, label.z, label.dd, label.vw, label.interior)
            Labale.add_registry_item(labelsrv.id, labelsrv)


def unload_module():
    print(f"Module {__name__} is being unloaded.")


atexit.register(unload_module)

init_module()

from . import commands
