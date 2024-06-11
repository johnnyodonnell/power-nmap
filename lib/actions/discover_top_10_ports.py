from lib.actions.lib.scan import run_scan
from lib.actions.lib.top_ports import get_top_10_ports, flatten_ports


def discover_and_scan_top_10_ports(current_state):
    output_filename = "discover_top_10_ports.xml"
    run_scan(
            [
                "-PS" + flatten_ports(get_top_10_ports()),
                "-oX", output_filename
                ],
            current_state["target"],
            output_filename,
            current_state)


