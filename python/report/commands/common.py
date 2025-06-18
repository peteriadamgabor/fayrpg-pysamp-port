from python.model.server import Player
from python.model.server import ReportCategory
from python.report.functions import send_report_emergency, send_report_msg

from python.dialogtree import ActionNode
from python.dialogtree import ListNode
from python.dialogtree import InputNode
from python.dialogtree import DialogTree


@Player.command
@Player.using_registry
def jelentes(player: Player):
    dialog_tree: DialogTree | None = DialogTree()
    report_list_node: ListNode = ListNode("report_list_node", "", "Kiválaszt", "Bezár", "Válassz kategórát")
    
    for value in ReportCategory.get_registry_items():
        if value.is_visible:
            input_node_content: str = f"{value.order}. {value.name}"
            input_node: InputNode = InputNode("input_node", "Írd le a mondani valódat", "Küldés", "Mégsem", "Jelentés", input_node_content)

            input_node.response_handler = send_report_msg
            input_node.response_handler_parameters = value.code,
            input_node.close_in_end = True

            report_list_node.add_child(input_node)

    emergency_node: ActionNode = ActionNode("emergency_node", display="Vészhelyzet")
    emergency_node.response_handler = send_report_emergency

    report_list_node.add_child(emergency_node)

    dialog_tree.add_root(report_list_node)
    dialog_tree.show_root_dialog(player)
