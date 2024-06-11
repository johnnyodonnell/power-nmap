from lib.actions.lib.scan import run_scan
from lib.actions.lib.top_ports import get_top_30_ports, flatten_ports


def discover_and_scan_top_30_ports(current_state):
    output_filename = "discover_top_30_ports.xml"
    run_scan(
            ["-p", flatten_ports(get_top_30_ports()), "-oX", output_filename],
            current_state["target"],
            output_filename,
            current_state)


