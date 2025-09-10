"""Módulo statistics.

Define la clase Statistics para recopilar y mostrar métricas de la red y dispositivos.
Integración de error_log para registrar errores en operaciones estadísticas.
"""

# Integración del sistema de log de errores
from ErrorLog import log_error
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

    def log_sent(self, command=None):
        """Incrementa el contador de paquetes enviados."""
        try:
            self.total_packets_sent += 1
        except Exception as e:
            log_error("StatisticsError", f"Error al registrar paquete enviado: {e}", command)

    def log_delivered(self, hops, device_name, command=None):
        """Registra un paquete entregado.

        Args:
            hops (int): Número de saltos del paquete.
            device_name (str): Nombre del dispositivo que procesó el paquete.
        """
        try:
            if not isinstance(hops, int) or hops < 0:
                log_error("StatisticsError", f"Número de saltos inválido: {hops}", command)
                return
            if not isinstance(device_name, str) or not device_name:
                log_error("StatisticsError", f"Nombre de dispositivo inválido: {device_name}", command)
                return
            self.delivered += 1
            self.hop_counts.append(hops)
            self.device_activity[device_name] = self.device_activity.get(device_name, 0) + 1
        except Exception as e:
            log_error("StatisticsError", f"Error al registrar entrega: {e}", command)

    def log_dropped_ttl(self, command=None):
        """Incrementa el contador de paquetes descartados por TTL expirado."""
        try:
            self.dropped_ttl += 1
        except Exception as e:
            log_error("StatisticsError", f"Error al registrar paquete descartado (TTL): {e}", command)

    def show_statistics(self, command=None):
        """Imprime en consola un reporte de las estadísticas acumuladas."""
        try:
            print(f"Total packets sent: {self.total_packets_sent}")
            print(f"Delivered: {self.delivered}")
            print(f"Dropped (TTL): {self.dropped_ttl}")
            avg_hops = self._calculate_average_hops()
            print(f"Average hops: {avg_hops}")
            if self.device_activity:
                top_talker = max(self.device_activity, key=self.device_activity.get)
                count = self.device_activity[top_talker]
                print(f"Top talker: {top_talker} (processed {count} packets)")
        except Exception as e:
            log_error("StatisticsError", f"Error mostrando estadísticas: {e}", command)

    def reset(self, command=None):
        """Restablece todas las estadísticas al estado inicial."""
        try:
            self.__init__()
        except Exception as e:
            log_error("StatisticsError", f"Error al resetear estadísticas: {e}", command)

    def _calculate_average_hops(self):
        """Calcula el promedio de saltos por paquete entregado.

        Returns:
            float: Promedio de saltos con dos decimales.
        """
        try:
            total = 0
            count = 0
            current = self.hop_counts.head
            while current:
                total += current.data
                count += 1
                current = current.next
            return round(total / count, 2) if count > 0 else 0
        except Exception as e:
            log_error("StatisticsError", f"Error calculando promedio de saltos: {e}")
            return 0
