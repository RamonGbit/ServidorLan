"""Módulo device.

Proporciona clases para representar dispositivos e interfaces de red.
"""

from DataStructures.LinkedList import LinkedList
from Comunication.Packet import PacketQueue
from Comunication.Packet import PacketHistory
from Routing.AVLRouteTable import AVLRouteTable

class Interface:
    """Representa una interfaz de red de un dispositivo.

    Attributes:
        name (str): Nombre de la interfaz.
        ip_address (Optional[str]): Dirección IP asignada.
        status (str): Estado de la interfaz ('up' o 'down').
        neighbors (LinkedList): Interfaces vecinas conectadas.
        packet_queue (PacketQueue): Cola de paquetes para el tick actual.
        next_packet_queue (PacketQueue): Cola de paquetes para el siguiente tick.
    """
    def __init__(self, name):
        """
        Inicializa una nueva interfaz de red.

        Args:
            name (str): Nombre de la interfaz.
        """
        self.name = name
        self.ip_address = None
        self.status = 'down'
        self.neighbors = LinkedList()
        self.packet_queue = PacketQueue()
        self.next_packet_queue = PacketQueue()

class Device:
    """Clase base para dispositivos de red.

    Attributes:
        name (str): Nombre del dispositivo.
        device_type (str): Tipo de dispositivo ('router', 'switch', 'host', 'firewall').
        interfaces (LinkedList): Lista de interfaces del dispositivo.
        online (bool): Indica si el dispositivo está online.
        packet_history (PacketHistory): Historial de paquetes procesados.
    """
    def __init__(self, name, device_type):
        """Inicializa un dispositivo de red.

        Args:
            name (str): Nombre del dispositivo.
            device_type (str): Tipo de dispositivo ('router', 'switch', 'host', 'firewall').
        """
        self.name = name
        self.device_type = device_type
        self.interfaces = LinkedList()
        self.online = True
        self.packet_history = PacketHistory()

    def receive_packet(self, packet, iface_name):
        """Recibe un paquete y lo encola en la interfaz especificada.

        Args:
            packet (Packet): Paquete a recibir.
            iface_name (str): Nombre de la interfaz receptora.

        Raises:
            ValueError: Si la interfaz no existe o el dispositivo está offline.
        """
        from ErrorLog import log_error
        iface = self.get_interface(iface_name)
        if not iface or not self.online:
            log_error('ConnectionError', 'Interfaz no encontrada o dispositivo offline', f'receive_packet iface={iface_name}')
            raise ValueError('Interfaz no encontrada o dispositivo offline')
        iface.packet_queue.enqueue(packet)

    def process_packets(self, statistics=None):
        """Procesa un paquete por interfaz para simular un salto de red.

        Si se proporciona statistics, registra entregas y descartes por TTL.

        Args:
            statistics (Statistics, opcional): Objeto para registrar métricas de red.
        """
        # Para evitar entregas duplicadas en el mismo tick
        seen_delivered = set()
        current_iface = self.interfaces.head
        # Procesar un único paquete por interfaz para simular un salto por tick
        while current_iface:
            iface = current_iface.data
            if not iface.packet_queue.is_empty():
                packet = iface.packet_queue.dequeue()
                # Determine if packet arrived at its destination
                arrived = False
                check_node = self.interfaces.head
                while check_node:
                    if check_node.data.ip_address == packet.destination_ip:
                        arrived = True
                        break
                    check_node = check_node.next
                if arrived:
                    # Entrega única por tick
                    if packet.packet_id not in seen_delivered:
                        seen_delivered.add(packet.packet_id)
                        self.packet_history.push(packet)
                        if statistics:
                            hops = packet.route_trace.size
                            statistics.log_delivered(hops, self.name)
                        print(f"[Tick] {self.name}: packet delivered (TTL={packet.ttl})")
                else:
                    # TTL y traza
                    packet.ttl -= 1
                    packet.add_hop(self.name)
                    if packet.ttl > 0:
                        # Historial de procesamiento
                        self.packet_history.push(packet)
                        # Forward packet solo al primer vecino (un solo salto por tick)
                        first_neighbor = iface.neighbors.head
                        if first_neighbor:
                            neighbor_iface = first_neighbor.data
                            neighbor_iface.next_packet_queue.enqueue(packet)
                            print(f"[Tick] {self.name} → {neighbor_iface.name}: packet forwarded (TTL={packet.ttl})")
                    else:
                        if statistics:
                            statistics.log_dropped_ttl()
                        print(f"[Tick] {self.name}: packet dropped (TTL expired)")
            current_iface = current_iface.next

    def show_history(self):
        """Muestra el historial de paquetes procesados por el dispositivo.

        Cada entrada incluye ruta de salto y TTL al arribo.
        """
        print(f"Historial de {self.name}:")
        current = self.packet_history.top
        while current:
            pkt = current.data
            print(f"Packet from {pkt.source_ip} to {pkt.destination_ip}: '{pkt.content}' | TTL at arrival: {pkt.ttl}")
            pkt.show_trace()
            current = current.next

    def show_queue(self):
        """Muestra los paquetes pendientes en la cola de cada interfaz.

        Cada entrada detalla el ID, IP origen, IP destino y TTL.
        """
        print(f"Pending queue for {self.name}:")
        current_iface = self.interfaces.head
        has_any = False
        while current_iface:
            iface = current_iface.data
            queue = iface.packet_queue
            if not queue.is_empty():
                has_any = True
                print(f" Interface {iface.name}:")
                node = queue.front
                while node:
                    pkt = node.data
                    print(f"  Packet {pkt.packet_id}: from {pkt.source_ip} to {pkt.destination_ip}, TTL={pkt.ttl}")
                    node = node.next
            current_iface = current_iface.next
        if not has_any:
            print("  (empty)")
    def show_interfaces(self):
        """Muestra las interfaces del dispositivo con IP y estado.

        Si no hay interfaces, indica '(none)'.
        """
        print(f"Interfaces for {self.name}:")
        current = self.interfaces.head
        if not current:
            print("  (none)")
        while current:
            iface = current.data
            print(f"  {iface.name} - IP: {iface.ip_address or 'unassigned'} - Status: {iface.status}")
            current = current.next

    def add_interface(self, interface_name):
        """Agrega una nueva interfaz al dispositivo.

        Args:
            interface_name (str): Nombre de la interfaz.
        """
        self.interfaces.append(Interface(interface_name))

    def set_status(self, status):
        """Cambia el estado del dispositivo.

        Args:
            status (str): 'online' o 'offline'.

        Raises:
            ValueError: Si el estado no es válido.
        """
        if status not in ['online', 'offline']:
            raise ValueError('Estado inválido')
        self.online = (status == 'online')

    def get_interface(self, name):
        """Retorna la interfaz especificada si existe.

        Args:
            name (str): Nombre de la interfaz.

        Returns:
            Interface | None: La interfaz encontrada o None.
        """
        current = self.interfaces.head
        while current:
            if current.data.name == name:
                return current.data
            current = current.next
                # processing packet


class Router(Device):
    """Dispositivo de tipo router.

    Args:
        name (str): Nombre del router.
    """
    def __init__(self, name, policy_trie=None):
        """
        Inicializa un router.

        Args:
            name (str): Nombre del router.
        """
        super().__init__(name, 'router')
        self.route_table = AVLRouteTable()
        self.policy_trie = policy_trie
    def process_packets(self, statistics=None):
        from ErrorLog import log_error
        seen_delivered = set()
        current_iface = self.interfaces.head
        while current_iface:
            iface = current_iface.data
            if not iface.packet_queue.is_empty():
                packet = iface.packet_queue.dequeue()
                # Chequeo de políticas antes de cualquier reenvío
                policy = None
                if self.policy_trie:
                    policy = self.policy_trie.get_policy(packet.destination_ip)
                if policy:
                    if 'block' in policy and policy['block']:
                        if statistics:
                            statistics.log_dropped_policy()
                        log_error('PolicyError', f"Paquete bloqueado por política en router {self.name}", f"dest={packet.destination_ip}")
                        print(f"[Tick] {self.name}: packet dropped (policy block)")
                        current_iface = current_iface.next
                        continue
                    if 'ttl-min' in policy and packet.ttl < policy['ttl-min']:
                        if statistics:
                            statistics.log_dropped_policy()
                        log_error('PolicyError', f"Paquete descartado por TTL menor a política en router {self.name}", f"dest={packet.destination_ip} ttl={packet.ttl}")
                        print(f"[Tick] {self.name}: packet dropped (policy ttl-min)")
                        current_iface = current_iface.next
                        continue
                arrived = False
                check_node = self.interfaces.head
                while check_node:
                    if check_node.data.ip_address == packet.destination_ip:
                        arrived = True
                        break
                    check_node = check_node.next
                if arrived:
                    if packet.packet_id not in seen_delivered:
                        seen_delivered.add(packet.packet_id)
                        self.packet_history.push(packet)
                        if statistics:
                            hops = packet.route_trace.size
                            statistics.log_delivered(hops, self.name)
                        print(f"[Tick] {self.name}: packet delivered (TTL={packet.ttl})")
                else:
                    packet.ttl -= 1
                    packet.add_hop(self.name)
                    if packet.ttl > 0:
                        self.packet_history.push(packet)
                        first_neighbor = iface.neighbors.head
                        if first_neighbor:
                            neighbor_iface = first_neighbor.data
                            neighbor_iface.next_packet_queue.enqueue(packet)
                            print(f"[Tick] {self.name} → {neighbor_iface.name}: packet forwarded (TTL={packet.ttl})")
                    else:
                        if statistics:
                            statistics.log_dropped_ttl()
                        log_error('TTLExpired', f"Paquete descartado por TTL expirado en router {self.name}", f"dest={packet.destination_ip} ttl=0")
                        print(f"[Tick] {self.name}: packet dropped (TTL expired)")
            current_iface = current_iface.next


class Switch(Device):
    """Dispositivo de tipo switch.

    Args:
        name (str): Nombre del switch.
    """
    def __init__(self, name):
        """
        Inicializa un switch.

        Args:
            name (str): Nombre del switch.
        """
        super().__init__(name, 'switch')


class Host(Device):
    """Dispositivo de tipo host.

    Args:
        name (str): Nombre del host.
    """
    def __init__(self, name):
        """
        Inicializa un host.

        Args:
            name (str): Nombre del host.
        """
        super().__init__(name, 'host')


class Firewall(Device):
    """Dispositivo de tipo firewall.

    Args:
        name (str): Nombre del firewall.
    """
    def __init__(self, name):
        """
        Inicializa un firewall.

        Args:
            name (str): Nombre del firewall.
        """
        super().__init__(name, 'firewall')
