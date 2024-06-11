from lib.actions.lib.scan import run_scan
from lib.actions.lib.top_ports import get_top_2_ports, flatten_ports


def discover_and_scan_top_2_ports(current_state):
    output_filename = "discover_top_2_ports.xml"
    port_list = get_top_2_ports()
    run_scan(
            ["-p", flatten_ports(port_list), "-oX", output_filename],
            current_state["target"],
            output_filename,
            current_state,
            port_list)


