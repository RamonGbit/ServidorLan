"""Módulo packet.

Define clases para el manejo de paquetes en la red:
- Packet: representa un paquete y su rastro de ruta.
- PacketQueue: cola de paquetes.
- PacketHistory: pila de historial de paquetes.
"""

from DataStructures.Stack import Stack
from DataStructures.Queue import Queue
from DataStructures.LinkedList import LinkedList


class Packet:
    """Representa un paquete y su rastro de ruta.

    Esta clase permite crear y gestionar un paquete que viaja a través de la red.
    """

    def __init__(self, packet_id, source_ip, destination_ip, content, time_to_live):
        """Inicializa un nuevo paquete.

        Args:
            packet_id (str): Identificador único del paquete.
            source_ip (str): Dirección IP de origen.
            destination_ip (str): Dirección IP de destino.
            content (str): Contenido del paquete.
            time_to_live (int): Tiempo de vida inicial.
        """
        self.packet_id = packet_id
        self.source_ip = source_ip
        self.destination_ip = destination_ip
        self.content = content
        self.time_to_live = time_to_live
        self.route_trace = LinkedList()

    def add_hop(self, device_name):
        """Agrega un salto al rastro de ruta.

        Args:
            device_name (str): Nombre del dispositivo por el que pasa el paquete.
        """
        self.route_trace.append(device_name)

    def show_trace(self):
        """Imprime el rastro de ruta del paquete en consola.

        Esta función muestra en consola el recorrido de los dispositivos por los que ha pasado el paquete.
        """
        hops = []
        current = self.route_trace.head
        while current:
            hops.append(current.data)
            current = current.next
        print(f"Path: {' -> '.join(hops)}")
    
    @property
    def ttl(self):
        """Alias para time_to_live.

        Returns:
            int: Tiempo de vida restante del paquete.
        """
        return self.time_to_live

    @ttl.setter
    def ttl(self, value):
        """Establece el tiempo de vida restante del paquete.

        Args:
            value (int): Nuevo TTL.
        """
        self.time_to_live = value


class PacketQueue(Queue):
    """Cola de paquetes para un dispositivo o interfaz.

    Esta clase hereda de Queue para gestionar paquetes en una cola.
    """
    pass


class PacketHistory(Stack):
    """Historial de paquetes recibidos.

    Esta clase hereda de Stack para gestionar el historial de paquetes en una pila.
    """
    pass
