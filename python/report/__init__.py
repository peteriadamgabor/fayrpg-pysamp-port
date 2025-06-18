import atexit

from sqlalchemy import select

from python.database.context_managger import transactional_session
from python.server.database import MAIN_SESSION
from python.model.database import ReportCategory as ReportCategoryDB
from python.model.server import ReportCategory

from .commands import common, admin


def init_module():
    """
    This function is called when the module is first loaded.
    """
    print(f"Module {__name__} is being initialized.")
    
    with transactional_session(MAIN_SESSION) as session:
        categories = session.scalars(select(ReportCategoryDB).order_by(ReportCategoryDB.order)).all()

        for category in categories:
            ReportCategory.add_registry_item(category.code , ReportCategory(**category.to_dict()))

def cleanup_module():
    """
    This function is called when the program is exiting.
    """
    print(f"Module {__name__} is being unloaded.")


atexit.register(cleanup_module)

init_module()
