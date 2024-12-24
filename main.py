import os
import json
import threading
import sys
import signal
import shutil
import logical.wire as wire
import socket

def signal_handler(sig, frame):
    print("\nExiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
class connection():
    def __init__(self, port, switch_ip, logical_port, vlan, mac):
        self.port = port
        self.switch_ip = switch_ip
        self.client_socket = None
        self.logical_port = logical_port
        self.vlan = vlan
        self.mac = mac

    def _generate_packet(self, data):
        return {
            "data": data,
            "from": self.port,
            "destination": self.ip_destination,
            "vlan_id": self.vlan,
            "destination_mac": self.mac,
        }
class Switch():
    def __init__(self):
        self.___switch_ip = "127.0.0.1"
        self.___switch_port = 40000
        self.switch_logical_ports = [1, 2, 3, 4, 5, 6]
        self.switch_physical_linked_ports = {
            1: 40001,
            2: 40002,
            3: 40003,
            4: 40004,
            5: 40005,
            6: 40006,
        }

        self.connections_map = {}
        self._configurations_files = {
            "_used_switch_ports_and_who": "./config/used_ports.json",
            "_mac_table": "./config/mac_table.json",
            "_switch_interfaces": "./config/interfaces.json",
            "_arp_table": "./config/arp_table.json",
            "_transmision_logs": "./config/transmission_packet_logs.json",
            "_profile": "./config/profile.json"
        }
        self._used_switch_ports_and_who = {}
        self._mac_table = {}
        self._switch_interfaces = {}
        self.__mac_address = "86:73:6a:65:ca:36"
        self._arp_table = {}
        self._transmision_logs = {}
    ## INITIALIZE THE SWITCH LISTENING THREADS
    def _start_switch_listening(self): ## INITIALIZE THE SWITCH LISTENING THREADS
        threads = []
        for port in self.switch_physical_linked_ports.values():
            thread = threading.Thread(target=self._listen, args=(port,))
            thread.daemon = True  # Permite que los hilos terminen al cerrar el programa
            thread.start()
            threads.append(thread)
        #print("All listening threads started.")

    ## LISTEN TO THE PORTS AND HANDLE THE CONNECTIONS
    def _listen(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((self.___switch_ip, port))
                s.listen()
                print(f"Switch escuchando en el puerto {port}")
                while True:
                    conn, addr = s.accept()
                    print(f"Conexión establecida con {addr}")
                    with conn:
                        try:
                            # Enviar datos iniciales
                            initial_data = {
                                "name": "switch1",
                                "port": port,
                                "type": "switch",
                                "vlan": 1,
                                "mac": self.__mac_address
                            }
                            conn.sendall(json.dumps(initial_data).encode())
                            print(f"Datos iniciales enviados a {addr}: {initial_data}")

                            # Manejo continuo de datos
                            while True:
                                data = conn.recv(1024)
                                if not data:
                                    print(f"Conexión cerrada por {addr}")
                                    break

                                raw_data = data.decode()
                                print(f"Datos recibidos de {addr}: {raw_data}")

                        except socket.error as e:
                            print(f"Error de socket con {addr}: {e}")

            except Exception as e:
                print(f"Error escuchando en el puerto {port}: {e}")

    ## ROUTE THE PACKETS TO THE DESTINATION
    def _route(self, packet):
        destination_ip = packet.get("destination_ip")
        if destination_ip in self._mac_table:
            destination_mac = self._mac_table[destination_ip]
            packet["destination_mac"] = destination_mac
            print(f"Packet sent to {destination_ip} with MAC address {destination_mac}")
        else:
            print(f"Destination IP {destination_ip} not found in the ARP table")

    ## COMMANDS
    def _add_interface(self, name, ip_address, logical_port):
        self._switch_interfaces[name] = [ip_address, logical_port]
        print(f"Interface {name} added with IP address {ip_address} and port {logical_port}")
        
        _switch_interfaces_config_file = self._configurations_files["_switch_interfaces"]
        interfaces_last_data = {}

        if os.path.exists(_switch_interfaces_config_file):
            with open(_switch_interfaces_config_file, "r") as interfaces_file:
                try:
                    interfaces_last_data = json.load(interfaces_file)
                except json.JSONDecodeError:
                    pass

        interfaces_last_data.update(self._switch_interfaces)

        with open(_switch_interfaces_config_file, "w") as interfaces_file:
            json.dump(interfaces_last_data, interfaces_file, indent=4)

        _switch_ports_config = self._configurations_files["_used_switch_ports_and_who"]
        if os.path.exists(_switch_ports_config):
            with open(_switch_ports_config, "r") as ports_config_file:
                ports_status_asign_config = json.load(ports_config_file)

            port_number = f"port_{logical_port}"
            if port_number in ports_status_asign_config["ports"]:
                ports_status_asign_config["ports"][port_number]["port_status"] = "UP"
                ports_status_asign_config["ports"][port_number]["port_asign"] = name
                ports_status_asign_config["ports"][port_number]["port_local"] = self.switch_physical_linked_ports[int(logical_port)]
                with open(_switch_ports_config, "w") as ports_config_file:
                    json.dump(ports_status_asign_config, ports_config_file, indent=4)
                print(f"Port {port_number} status set to UP and assigned to {name}")
            else:
                print(f"Port {port_number} does not exist in the configuration.")

    def _show_interfaces(self):
        print("Interfaces:")
        for interface, values in self._switch_interfaces.items():
            print(f"Interface {interface}: IP address: {values[0]}, logical port: {values[1]}")

    def _show_ports(self):
        print("Logical ports:")
        with open(self._configurations_files["_used_switch_ports_and_who"], 'r') as ports_data:
            try:
                ports_data_from_json = json.load(ports_data)
                for port_key, port_info in ports_data_from_json["ports"].items():
                    print(f"Logical port {port_key}:\n \\-- STATUS: {port_info['port_status']} \n     PORT MAC: {port_info['port_mac']}\n     VLAN ID: {port_info['port_vlan_id']}\n     ASIGNED TO: {port_info['port_asign']}\n     LOCAL PORT: {port_info['port_local']}")
            except json.JSONDecodeError:
                print("Error loading ports data. The file may be corrupted or invalid.")

    def _add_arp_entry(self, ip_address, mac_address):
        self._mac_table[ip_address] = mac_address
        print(f"ARP entry added for IP address {ip_address} with MAC address {mac_address}")

class Utilities():
    def _check_last_configuration(self):
        with open("./config/profile.json", "r") as profile:
            profile_data = json.load(profile)
            if profile_data["profile_info"]["last_config"]:
                return True
            else:
                os.makedirs("./config.bck", exist_ok=True)
                for file in ["interfaces.json", "used_ports.json", "mac_table.json", "arp_table.json"]:
                    shutil.copy(f"./config/{file}", f"./config.bck/{file}")

                for file in ["interfaces.json", "mac_table.json", "arp_table.json"]:
                    with open(f"./config/{file}", "w") as config_file:
                        json.dump({}, config_file, indent=4)
                return False

    def _load_last_configuration(self, switch):
        with open(switch._configurations_files['_switch_interfaces']) as interfaces_last_config_file:
            switch._switch_interfaces = json.load(interfaces_last_config_file)
        with open(switch._configurations_files['_used_switch_ports_and_who']) as used_ports_last_config_file:
            switch._used_switch_ports_and_who = json.load(used_ports_last_config_file)
        with open(switch._configurations_files['_mac_table']) as mac_table_last_config_file:
            switch._mac_table = json.load(mac_table_last_config_file)
        with open(switch._configurations_files['_arp_table']) as arp_table_last_config_file:
            switch._arp_table = json.load(arp_table_last_config_file)

if __name__ == "__main__":
    switch = Switch()
    utilities = Utilities()
    last_configuration = utilities._check_last_configuration()
    switch._start_switch_listening()
    with open(switch._configurations_files['_profile'], "r") as profile_to_get_prompt:
        profile_to_get_prompt = json.load(profile_to_get_prompt)
        user_name = profile_to_get_prompt["switch_info"]["user_name"]
        prompt = f"{user_name}@switch1> "

    if last_configuration:
        print("Last configuration found. Do you want to load it? (y/n)")
        load_last_configuration = input(prompt)
        if load_last_configuration.lower() == "y":
            print("Loading last configuration...")
            utilities._load_last_configuration(switch)
        else:
            print("Creating new configuration...")

    while True:
        command = input(prompt)
        if command.lower() == "exit":
            print("There is a configuration to save. Do you want to save this configuration? (y/n)")
            save_configuration = input(prompt)
            
            try:
                with open("./config/profile.json", "r") as profile:
                    profile_data = json.load(profile)
            except (FileNotFoundError, json.JSONDecodeError):
                profile_data = {
                    "switch_info": {
                        "sw_name": "switch1",
                        "user_name": "sw_user",
                        "sw_mac_address": "86:73:6a:65:ca:36"
                    },
                    "profile_info": {
                        "last_config": False
                    }
                }

            profile_data["profile_info"]["last_config"] = (save_configuration.lower() == "y")

            with open("./config/profile.json", "w") as profile:
                json.dump(profile_data, profile, indent=4)

            print("Configuration saved." if save_configuration.lower() == "y" else "Configuration not saved (User's choice).")
            break

        elif command.lower() == "help":
            print("Commands:")
            print("show ports")
            print("add interface <name> <ip_address> <port>")
            print("add arp <ip_address> <mac_address>")
            print("show interfaces")
            print("show arp")
            print("delete arp <ip_address>")
        elif command.startswith("show mac"):
            print("MAC Address: ", switch.__mac_address)
        elif command.startswith("whoami"):
            print(user_name)
        elif command.startswith("show ports"):
            switch._show_ports()
        elif command.startswith("add interface"):
            try:
                _, _, name, ip, port = command.split()
                switch._add_interface(name, ip, port)
            except ValueError:
                print("Usage: add interface <name> <ip_address> <port>")
        elif command.startswith("add arp"):
            try:
                _, _, ip, mac = command.split()
                switch._add_arp_entry(ip, mac)
            except ValueError:
                print("Usage: add arp <ip_address> <mac_address>")
        elif command == "show interfaces":
            switch._show_interfaces()
        else:
            print("Invalid command. Type 'help' to see the available commands.")
