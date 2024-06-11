
def always_true(host):
    return True

def generate_port_not_scanned_constraint(port_list):
    return lambda host:
        if not "ports_scanned" in host:
            return True

        ports_scanned = host["ports_scanned"]
        for port in port_list:
            if (not port in ports_scanned) or (not ports_scanned[port]):
                return True

        return False

def get_remaining_hosts(port_list):
    return get_active_hosts(
            current_state,
            generate_port_not_scanned_constraint(port_list))

def get_active_hosts(current_state, additional_constraint = always_true):
    active_hosts = []
    if "hosts" in current_state:
        hosts = current_state["hosts"]
        for address in hosts:
            host = hosts[address]
            if (host["status"] == "up") and additional_constraint(host):
                active_hosts.append(address)
    return active_hosts

