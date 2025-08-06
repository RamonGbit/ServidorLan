"""Módulo statistics.

Define la clase Statistics para recopilar y mostrar métricas de la red y dispositivos.
"""
from DataStructures.LinkedList import LinkedList

class Statistics:
    """Gestiona estadísticas de paquetes en la red.

    Esta clase recopila métricas de paquetes enviados, entregados y descartados,
    y mantiene conteo de saltos y actividad por dispositivo.
    """
    def __init__(self):
        """Inicializa contadores y estructuras de datos.

        Establece contadores en cero y crea estructuras para registrar saltos y actividad.
        """
        self.total_packets_sent = 0
        self.delivered = 0
        self.dropped_ttl = 0
        self.hop_counts = LinkedList()
        self.device_activity = {}

    def log_sent(self):
        """Incrementa el contador de paquetes enviados."""
        self.total_packets_sent += 1

    def log_delivered(self, hops, device_name):
        """Registra un paquete entregado.

        Args:
            hops (int): Número de saltos del paquete.
            device_name (str): Nombre del dispositivo que procesó el paquete.
        """
        self.delivered += 1
        self.hop_counts.append(hops)
        self.device_activity[device_name] = self.device_activity.get(device_name, 0) + 1

    def log_dropped_ttl(self):
        """Incrementa el contador de paquetes descartados por TTL expirado."""
        self.dropped_ttl += 1

    def show_statistics(self):
        """Imprime en consola un reporte de las estadísticas acumuladas."""
        print(f"Total packets sent: {self.total_packets_sent}")
        print(f"Delivered: {self.delivered}")
        print(f"Dropped (TTL): {self.dropped_ttl}")
        avg_hops = self._calculate_average_hops()
        print(f"Average hops: {avg_hops}")
        if self.device_activity:
            top_talker = max(self.device_activity, key=self.device_activity.get)
            count = self.device_activity[top_talker]
            print(f"Top talker: {top_talker} (processed {count} packets)")

    def reset(self):
        """Restablece todas las estadísticas al estado inicial."""
        self.__init__()

    def _calculate_average_hops(self):
        """Calcula el promedio de saltos por paquete entregado.

        Returns:
            float: Promedio de saltos con dos decimales.
        """
        total = 0
        count = 0
        current = self.hop_counts.head
        while current:
            total += current.data
            count += 1
            current = current.next
        return round(total / count, 2) if count > 0 else 0
