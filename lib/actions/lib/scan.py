import os
import re
import subprocess
import threading
import time
import xml.etree.ElementTree as ET

from threading import Thread

from lib.state import save_state


# From https://stackoverflow.com/a/325528
class ReadOutputThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, output_filename, current_state, port_list):
        # https://stackoverflow.com/a/11816038
        super(ReadOutputThread, self).__init__(daemon=True)

        self.output_filename = output_filename
        self.current_state = current_state
        self.port_list = port_list
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        while not self.stopped():
            if os.path.isfile(self.output_filename):
                try:
                    copy_output_to_state(
                            self.output_filename,
                            self.current_state,
                            self.port_list)
                except Exception as e:
                    print("Error copying output to state")
                    print(e)
            time.sleep(5)
        copy_output_to_state(
                self.output_filename,
                self.current_state,
                self.port_list)
        print("Scan output processed")


def run_scan(args, target, output_filename, current_state, port_list = []):
    read_output = ReadOutputThread(output_filename, current_state, port_list)
    read_output.start()

    command = [
            "sudo", "nmap", "-v",
            "--max-scan-delay", "5ms", "--max-retries", "1",
            ]
    command += args
    if type(target) is list:
        command += target
    elif os.path.isfile(target):
        command += ["-iL", target]
    else:
        command.append(target)
    subprocess.run(command)
    read_output.stop()
    read_output.join()

def process_host(port_list, host_map, host):
    address = host.find("address").get("addr")

    state = host.find("status").get("state")
    if state == "up":
        if not address in host_map:
            host_map[address] = {}
        host_map[address]["status"] = "up"

        if not "ports_scanned" in host_map[address]:
            host_map[address]["ports_scanned"] = {}
        for port in port_list:
            host_map[address]["ports_scanned"][port] = True

    ports = host.find("ports")
    if ports is not None:
        ports = ports.findall("port")
        if not "ports" in host_map[address]:
            host_map[address]["ports"] = {}
        if not "tcp" in host_map[address]["ports"]:
            host_map[address]["ports"]["tcp"] = {}
        for port in ports:
            portid = port.get("portid")
            if not portid in host_map[address]["ports"]["tcp"]:
                host_map[address]["ports"]["tcp"][portid] = {}
            state = port.find("state")
            if state is not None:
                state = state.get("state")
                if state:
                    host_map[address]["ports"]["tcp"][portid]["state"] = state
            service = port.find("service")
            if service is not None:
                if not "service" in host_map[address]["ports"]["tcp"][portid]:
                    host_map[address]["ports"]["tcp"][portid]["service"] = {}
                name = service.get("name")
                product = service.get("product")
                version = service.get("version")
                if name is not None:
                    host_map[address]["ports"]["tcp"][portid]["service"]["name"] = name
                if product is not None:
                    host_map[address]["ports"]["tcp"][portid]["service"]["product"] = product
                if version is not None:
                    host_map[address]["ports"]["tcp"][portid]["service"]["version"] = version

def copy_output_to_state(output_filename, current_state, port_list):
    if not "hosts" in current_state:
        current_state["hosts"] = {}

    host_map = current_state["hosts"]
    with open(output_filename) as f:
        raw = f.read()
        # Handle bug with how nmap adds `</nmaprun>` tags
        xml = re.sub(r"</nmaprun>", "", raw)
        xml += "</nmaprun>"
        tree = ET.fromstring(xml)
        hosthints = tree.findall("hosthint")
        for hosthint in hosthints:
            process_host([], host_map, hosthint)
        hosts = tree.findall("host")
        for host in hosts:
            process_host(port_list, host_map, host)
    save_state(current_state)

