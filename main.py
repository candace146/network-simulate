import os
import socket
import json
import time
import threading
import random
import sys
import signal

def signal_handler(sig, frame):
    print("\nExiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

class switch():
    def __init__(self):
        self._configurations_files = {"_used_switch_ports_and_who": ".\\configurations\\used_ports.json",
                                      "_mac_table": ".\\configurations\\mac_table.json",
                                      "_switch_interfaces": ".\\configurations\\interfaces.json",
                                      "_arp_table": ".\\configurations\\arp_table.json",
                                      "_transmision_logs": ".\\configurations\\transmision_packet_logs.json"}
        self._used_switch_ports_and_who = {}
        self._mac_table = {}
        self._switch_interfaces = {}

    def _add_interface(self, name, ip_address, port):
        self._switch_interfaces[name] = [ip_address, port]
        print(f"Interface {name} added with IP address {ip_address} and port {port}")
        self._used_switch_ports_and_who[port] = ['UP', name]
        ## Write to json file append data
        _switch_interfaces_config_file = self._configurations_files["_switch_interfaces"]
        if os.path.exists(_switch_interfaces_config_file):
            with open(_switch_interfaces_config_file, "r") as interfaces_file:
                try:
                    interfaces_last_data = json.load(interfaces_file)
                except json.JSONDecodeError:
                    interfaces_last_data = {}
        else:
            interfaces_data = {}
        
        interfaces_last_data.update(self._switch_interfaces)
        with open(_switch_interfaces_config_file, "w") as interfaces_file:
            json.dump(interfaces_last_data, interfaces_file)





    def _show_interfaces(self):
        print("Interfaces:")
        for interface, values in self._switch_interfaces.items():
            print(f"Interface {interface}: IP address: {values[0]}, port {values[1]}")

    def _show_ports(self):
        print("Ports:")
        for port, values in self._used_switch_ports_and_who.items():
            print(f"Port {port}:\n \\-- STATUS: {values[0]} ASIGNED TO: {values[1]}")

    def _add_arp_entry(self, ip_address, mac_address):
        self._mac_table[ip_address] = mac_address
        print(f"ARP entry added for IP address {ip_address} with MAC address {mac_address}")


class utilities():
    def _check_last_configuration(self):
        with open(".\\config\\profile.json", "r") as profile:
            profile = json.load(profile)
            return profile.get("last_config", False)
        
    def _load_last_configuration(self):
        print("Loading")


if __name__ == "__main__":
    utilities = utilities()
    last_configuration = utilities._check_last_configuration()
    if last_configuration == True:
        print("Last configuration found. Do you want to load it? (y/n)")
        load_last_configuration = input("> ")
        if load_last_configuration.lower() == "y":
            print("Loading last configuration...")
            utilities._load_last_configuration()
            with open(".\\config\\profile.json", "r") as profile:
                profile = json.load(profile)
        else:
            print("Creating new configuration...")
    switch = switch()
    print("**********************************")
    print("        switch simulation         ")
    print("**********************************")
    while True:
        command = input("> ")
        if command.lower() == "exit":
            print("Exiting...")
            break
        elif command.lower() == "help":
            print("Commands:")
            print("show ports")
            print("add interface <name> <ip_address> <port>")
            print("add arp <ip_address> <mac_address>")
            print("show interfaces")
            print("show arp")
            print("delete arp <ip_address>")
        elif command.startswith("show ports"):
            switch._show_ports()
        elif command.startswith("add interface"):
            try:
                _, _, name, ip, port = command.split()
                switch._add_interface(name, ip, port)
            except ValueError:
                print("Uso: add interface <name> <ip_address> <port>")
        elif command.startswith("add arp"):
            try:
                _, _, ip, mac = command.split()
                switch._add_arp_entry(ip, mac)
            except ValueError:
                print("Uso: add arp <ip_address> <mac_address>")
        elif command == "show interfaces":
            switch._show_interfaces()
        elif command == "show arp":
            switch.show_arp_table()
        elif command.startswith("delete arp"):
            try:
                _, _, ip = command.split()
                switch.delete_arp_entry(ip)
            except ValueError:
                print("Uso: delete arp <ip_address>")

        else: 
            print("Invalid command. Type 'help' to see the available commands.")