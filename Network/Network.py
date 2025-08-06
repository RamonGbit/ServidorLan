"""Módulo network.

Proporciona la clase Network para gestionar la topología y conexiones de dispositivos.
"""

from DataStructures.LinkedList import LinkedList
from Comunication.Packet import Packet
from Comunication.Packet import PacketQueue
from Network.Device import Device

class Network:
    """Gestiona la topología y conexiones de dispositivos en la red.

    Attributes:
        devices (LinkedList): Lista de dispositivos en la red.
    """
    def __init__(self):
        """Inicializa la instancia de Network con lista de dispositivos vacía."""
        self.devices = LinkedList()

    def add_device(self, device):
        """Agrega un dispositivo a la red.

        Args:
            device (Device): Objeto de dispositivo a agregar.
        """
        self.devices.append(device)

    def find_device(self, name):
        """Busca un dispositivo por nombre.

        Args:
            name (str): Nombre del dispositivo.

        Returns:
            Device or None: El dispositivo si existe, sino None.
        """
        current = self.devices.head
        while current:
            if current.data.name == name:
                return current.data
            current = current.next
        return None

    def _get_device(self, name):
        """Retorna un dispositivo o lanza error si no existe.

        Args:
            name (str): Nombre del dispositivo.

        Returns:
            Device: El dispositivo encontrado.

        Raises:
            ValueError: Si el dispositivo no existe.
        """
        device = self.find_device(name)
        if not device:
            raise ValueError(f'Dispositivo {name} no encontrado')
        return device

    def _get_interface(self, device_name, interface_name):
        """Retorna una interfaz o lanza error si no existe.

        Args:
            device_name (str): Nombre del dispositivo.
            interface_name (str): Nombre de la interfaz.

        Returns:
            Interface: La interfaz encontrada.

        Raises:
            ValueError: Si la interfaz no existe.
        """
        device = self._get_device(device_name)
        iface = device.get_interface(interface_name)
        if not iface:
            raise ValueError(f'Interfaz {interface_name} no encontrada en dispositivo {device_name}')
        return iface

    def connect(self, device1_name, interface1_name, device2_name, interface2_name):
        """Conecta dos interfaces bidireccionalmente.

        Args:
            device1_name (str): Nombre del primer dispositivo.
            interface1_name (str): Nombre de la interfaz del primer dispositivo.
            device2_name (str): Nombre del segundo dispositivo.
            interface2_name (str): Nombre de la interfaz del segundo dispositivo.
        """
        iface1 = self._get_interface(device1_name, interface1_name)
        iface2 = self._get_interface(device2_name, interface2_name)
        if not iface1.neighbors.find(iface2):
            iface1.neighbors.append(iface2)
        if not iface2.neighbors.find(iface1):
            iface2.neighbors.append(iface1)

    def disconnect(self, device1_name, interface1_name, device2_name, interface2_name):
        """Desconecta dos interfaces previamente conectadas.

        Args:
            device1_name (str): Nombre del primer dispositivo.
            interface1_name (str): Nombre de la interfaz del primer dispositivo.
            device2_name (str): Nombre del segundo dispositivo.
            interface2_name (str): Nombre de la interfaz del segundo dispositivo.
        """
        iface1 = self._get_interface(device1_name, interface1_name)
        iface2 = self._get_interface(device2_name, interface2_name)
        iface1.neighbors.remove(iface2)
        iface2.neighbors.remove(iface1)

    def list_devices(self):
        """Imprime la lista de dispositivos con su estado."""
        print('Devices in network:')
        current = self.devices.head
        while current:
            status = 'online' if current.data.online else 'offline'
            print(f'- {current.data.name} ({status})')
            current = current.next

    def set_device_status(self, device_name, status):
        """Cambia el estado de un dispositivo.

        Args:
            device_name (str): Nombre del dispositivo.
            status (str): Nuevo estado ('online' o 'offline').

        Raises:
            ValueError: Si el dispositivo no existe o el estado es inválido.
        """
        device = self._get_device(device_name)
        device.set_status(status)

    def show_device_history(self, device_name):
        """Muestra el historial de un dispositivo.

        Args:
            device_name (str): Nombre del dispositivo.

        Raises:
            ValueError: Si el dispositivo no existe.
        """
        device = self._get_device(device_name)
        device.show_history()

    def show_statistics(self, statistics):
        """Muestra estadísticas de la red o de dispositivos.

        Args:
            statistics: Objeto de estadísticas con método show_statistics().
        """
        statistics.show_statistics()
    def show_queue(self, device_name):
        """Muestra los paquetes en espera en la cola de un dispositivo.

        Args:
            device_name (str): Nombre del dispositivo.
        """
        device = self._get_device(device_name)
        device.show_queue()
    def show_interfaces(self, device_name):
        """Muestra las interfaces de un dispositivo.

        Args:
            device_name (str): Nombre del dispositivo.
        """
        device = self._get_device(device_name)
        device.show_interfaces()
    def show_connections(self, device_name):
        """Muestra las conexiones de un dispositivo.

        Args:
            device_name (str): Nombre del dispositivo.
        """
        device = self._get_device(device_name)
        print(f"Connections for {device.name}:")
        current_iface = device.interfaces.head
        has_any = False
        while current_iface:
            iface = current_iface.data
            neighbor_node = iface.neighbors.head
            while neighbor_node:
                neighbor_iface = neighbor_node.data
                dev_node = self.devices.head
                owner = None
                while dev_node and owner is None:
                    dev = dev_node.data
                    iface_check = dev.interfaces.head
                    while iface_check:
                        if iface_check.data is neighbor_iface:
                            owner = dev.name
                            break
                        iface_check = iface_check.next
                    dev_node = dev_node.next
                if owner:
                    print(f" {iface.name} -> {owner}:{neighbor_iface.name}")
                    has_any = True
                neighbor_node = neighbor_node.next
            current_iface = current_iface.next
        if not has_any:
            print(" (no connections)")

    def send_packet(self, source_name, source_interface, destination_ip, content, ttl):
        """Crea y envía un paquete desde un dispositivo e interfaz origen.

        Args:
            source_name (str): Nombre del dispositivo origen.
            source_interface (str): Nombre de la interfaz origen.
            destination_ip (str): Dirección IP de destino.
            content (str): Contenido del paquete.
            ttl (int): Tiempo de vida inicial del paquete.

        Raises:
            ValueError: Si el dispositivo o la interfaz origen no existen.
        """
        source_device = self._get_device(source_name)
        interface = self._get_interface(source_name, source_interface)
        packet_id = f"pkt_{source_name}_{source_interface}_{destination_ip}"
        packet = Packet(packet_id, interface.ip_address, destination_ip, content, ttl)
        source_device.receive_packet(packet, source_interface)

    def process_network(self, statistics=None):
        """Procesa todos los dispositivos de la red para simular un ciclo de reloj.

        Args:
            statistics (Statistics, opcional): Objeto para registrar métricas de red.
        """
        current = self.devices.head
        while current:
            device = current.data
            if device.online:
                if statistics:
                    device.process_packets(statistics)
                else:
                    device.process_packets()
            current = current.next
        dev_node = self.devices.head
        while dev_node:
            dev = dev_node.data
            iface_node = dev.interfaces.head
            while iface_node:
                iface = iface_node.data
                iface.packet_queue = iface.next_packet_queue
                iface.next_packet_queue = PacketQueue()
                iface_node = iface_node.next
            dev_node = dev_node.next
