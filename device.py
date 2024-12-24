import socket
import threading
import time
import signal
import sys
import json

def signal_handler(sig, frame):
    print('Saliendo del programa')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


class connection:
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
                

class Device:
    def __init__(self, name, physical_port):
        self.name = name
        self.physical_port = physical_port
        self.switch_ip = "127.0.0.1"
        self.client_socket = None

    def connect_to_switch(self):
        try:
            # Inicializa el socket y conecta al switch
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.switch_ip, self.physical_port))
            print(f"{self.name} conectado al puerto físico {self.physical_port}")

            # Datos iniciales a enviar
            first_data_to_switch = {
                "name": self.name,
                "port": self.physical_port,
                "type": "device",
                "vlan": 1,
                "mac": "02:02:02:02:02:01"
            }
            self.send_data(json.dumps(first_data_to_switch))  # Enviar como JSON
            print(f"{self.name} intercambiando datos iniciales con el switch")

            # Recibir datos iniciales del switch
            response = self.client_socket.recv(1024).decode()
            print(f"{self.name} recibió del switch: {response}")

            # Simula mantener la conexión activa (puedes personalizar esta parte)
            while True:
                command = input(f"{self.name} > Ingresa un mensaje ('exit' para salir): ")
                if command.lower() == 'exit':
                    print(f"{self.name} cerrando la conexión.")
                    break
                self.send_data(command)

        except socket.error as e:
            print(f"Error de socket en {self.name}: {e}")
        except Exception as e:
            print(f"Error inesperado en {self.name}: {e}")
        finally:
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
                print(f"{self.name} conexión cerrada.")

    def send_data(self, data):
        try:
            if not isinstance(self.client_socket, socket.socket):
                raise TypeError("client_socket no es un socket válido.")
            if self.client_socket:
                print(f"{self.name} enviando: {data}")
                self.client_socket.send(data.encode())
        except Exception as e:
            print(f"Error al enviar datos: {e}")


    def send_data(self, data):
        try:
            if not isinstance(self.client_socket, socket.socket):
                raise TypeError("client_socket no es un socket válido.")
            if self.client_socket:
                packet_context = {
                    "data": data,
                    "from": self.name,
                    "to": "switch",
                    "vlan": 1,
                    "mac": "02:02:02:02:02:01"
                }
                print(f"{self.name} enviando: {data}")
                self.client_socket.send(data.encode())
        except TypeError as e:
            print(f"Error de tipo: {e}")
        except socket.error as e:
            print(f"Error de socket al enviar datos: {e}")
        except Exception as e:
            print(f"Error inesperado al enviar datos: {e}")

    def receive_data(self):
        while True:
            try:
                data = self.client_socket.recv(1024)
                if data:
                    print(f"{self.name} recibió: {data.decode()}")
                    switch_info = data.decode()
                    switch_info["port"] = connection.port

            except Exception as e:
                print(f"Error en {self.name}: {e}")
                break

    def start_communication(self):
        threading.Thread(target=self.receive_data).start()
        while True:
            time.sleep(2)
            self.send_data(f"Hola desde {self.name}")


if __name__ == "__main__":
    device1 = Device("Device 1", 40001)
    device1.connect_to_switch()
    device1.start_communication()