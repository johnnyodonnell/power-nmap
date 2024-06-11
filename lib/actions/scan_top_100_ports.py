from lib.actions.lib.scan import run_scan
from lib.actions.lib.top_ports import get_top_100_ports, flatten_ports
from lib.actions.lib.utils import get_remaining_hosts


def scan_top_100_ports(current_state):
    output_filename = "top_100_ports.xml"
    port_list = get_top_100_ports()
    run_scan(
            [
                "-Pn", "-p", flatten_ports(port_list),
                "-oX", output_filename,
                ],
            get_remaining_hosts(current_state, port_list),
            output_filename,
            current_state,
            port_list)

