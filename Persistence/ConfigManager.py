"""Módulo Persistence.ConfigManager.

Proporciona la clase ConfigManager para guardar y cargar configuraciones de red en formato JSON.
"""
import json
from DataStructures.LinkedList import LinkedList
from Network.Device import Router, Switch, Host, Firewall

class ConfigManager:
    """
    Gestiona el guardado y carga de la configuración de la red.

    Métodos estáticos:
        save_running_config: Exporta configuración actual a archivo de texto.
        load_config: Carga y ejecuta comandos desde un archivo de texto.
    """
    """Gestiona el guardado y la carga de la configuración de la red en JSON.

    Métodos estáticos:
        save_running_config(network, filename): Guarda la configuración activa.
        load_config(network, filename): Carga la configuración desde un archivo JSON.
    """
    @staticmethod
    def save_running_config(network, filename="running-config.json"):
        """Guarda la configuración actual de la red en un archivo JSON.

        Args:
            network (Network): Objeto con la topología y dispositivos.
            filename (str): Nombre del archivo de salida.

        Returns:
            None
        """
        # Exportar a JSON
        data = {"devices": [], "connections": []}
        # Recorrer dispositivos e interfaces
        node = network.devices.head
        while node:
            dev = node.data
            dev_entry = {
                "name": dev.name,
                "device_type": dev.device_type,
                "online": dev.online,
                "interfaces": []
            }
            iface_node = dev.interfaces.head
            while iface_node:
                iface = iface_node.data
                dev_entry["interfaces"].append({
                    "name": iface.name,
                    "ip_address": iface.ip_address,
                    "status": iface.status
                })
                iface_node = iface_node.next
            data["devices"].append(dev_entry)
            node = node.next
        # Recorrer conexiones evitando duplicados
        seen = set()
        node = network.devices.head
        while node:
            dev = node.data
            iface_node = dev.interfaces.head
            while iface_node:
                iface = iface_node.data
                neighbor_node = iface.neighbors.head
                while neighbor_node:
                    nb = neighbor_node.data
                    # buscar owner del vecino
                    owner = None
                    d2 = network.devices.head
                    while d2 and owner is None:
                        dv = d2.data
                        in2 = dv.interfaces.head
                        while in2:
                            if in2.data is nb:
                                owner = (dv.name, in2.data.name)
                                break
                            in2 = in2.next
                        d2 = d2.next
                    if owner:
                        pair = (dev.name, iface.name, owner[0], owner[1])
                        rev = (owner[0], owner[1], dev.name, iface.name)
                        if pair not in seen and rev not in seen:
                            seen.add(pair)
                            data["connections"].append(list(pair))
                    neighbor_node = neighbor_node.next
                iface_node = iface_node.next
            node = node.next
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_config(network, filename):
        """Carga la configuración de la red desde un archivo JSON y reconstruye la topología.

        Args:
            network (Network): Objeto donde cargar la configuración.
            filename (str): Ruta del archivo JSON.

        Returns:
            None
        """
        # Cargar desde JSON
        with open(filename, 'r') as f:
            data = json.load(f)
        # Reiniciar red
        network.devices = LinkedList()
        # Mapear tipos a clases
        type_map = {
            'router': Router,
            'switch': Switch,
            'host': Host,
            'firewall': Firewall
        }
        # Crear dispositivos e interfaces
        for dev in data.get('devices', []):
            cls = type_map.get(dev.get('device_type'), Router)
            obj = cls(dev.get('name'))
            obj.online = dev.get('online', True)
            for iface in dev.get('interfaces', []):
                obj.add_interface(iface.get('name'))
                inf = obj.get_interface(iface.get('name'))
                inf.ip_address = iface.get('ip_address')
                inf.status = iface.get('status', 'down')
            network.add_device(obj)
        # Reconstruir conexiones
        for conn in data.get('connections', []):
            if len(conn) == 4:
                network.connect(conn[0], conn[1], conn[2], conn[3])
