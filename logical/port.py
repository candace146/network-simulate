def _generate_ports(port_number):
    _port_number = port_number
    _port_status = "DOWN"
    _port_type = "Access"
    _port_speed = "10/100/1000"
    _port_duplex = "Full"
    _port_vlan = "1"
    _port_mac = "00:00:00:00:00:00"
    _port_ip = ""
    print(f"Physical logical_port generated {port_number}\n Number: {_port_number} \n Status: {_port_status}\n Type: {_port_type} \n Speed:  {_port_speed}\n Duplex: {_port_duplex} \n MAC: {_port_mac}\n IP: {_port_ip}")


def _change_port_status(status, port_number):
    _port_status = status
    print(f"Port {port_number} status changed to {status}")