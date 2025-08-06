"""Módulo cli.

Interfaz de línea de comandos para el simulador de red LAN estilo router.
"""

# CLI principal y parser de comandos
from Network.Network import Network
from Network.Device import Router
from Network.Device import Router, Switch, Host, Firewall
from Statistics.Statistics import Statistics
from Cli.Prompts import PromptManager
from Persistence.ConfigManager import ConfigManager

class CLI:
    """Interfaz de línea de comandos para el simulador de red LAN estilo router.

    Attributes:
        network (Network): Gestor de topología de red.
        statistics (Statistics): Estadísticas de la red.
        prompt (PromptManager): Gestor del prompt interactivo.
        running (bool): Indicador de ciclo de ejecución.
        command_map (dict): Mapa de comandos a métodos manejadores.
    """
    def __init__(self):
        """Inicializa la CLI.

        Establece los componentes de la interfaz de comandos.

        Attributes:
            network (Network): Gestor de topología de red.
            statistics (Statistics): Estadísticas de la red.
            prompt (PromptManager): Gestor del prompt interactivo.
            running (bool): Indicador de ciclo de ejecución.
            command_map (dict): Mapa de comandos a métodos manejadores.
        """
        self.network = Network()
        self.statistics = Statistics()
        self.prompt = PromptManager()
        self.running = True

        self.command_map = {
            'quit': self._handle_quit,
            'exit': self._handle_exit,
            'enable': self._handle_enable,
            'disable': self._handle_disable,
            'configure terminal': self._handle_configure,
            'hostname': self._handle_hostname,
            'interface': self._handle_interface,
            'ip address': self._handle_ip_address,
            'no shutdown': self._handle_no_shutdown,
            'shutdown': self._handle_shutdown,
            'connect': self._handle_connect,
            'disconnect': self._handle_disconnect,
            'list_devices': self._handle_list_devices,
            'set_device_status': self._handle_set_device_status,
            'show history': self._handle_show_history,
            'show statistics': self._handle_show_statistics,
            'show interfaces': self._handle_show_interfaces,
            'show queue': self._handle_show_queue,
            'show connections': self._handle_show_connections,
            'tick': self._handle_tick,
            'process': self._handle_tick,
            'send': self._handle_send,
            'save': self._handle_save,
            'load': self._handle_load,
        }

    def run(self):
        """Inicia el bucle principal de la CLI.

        Muestra el prompt y procesa los comandos hasta que `self.running` sea False.

        Returns:
            None
        """
        print("Bienvenido al simulador de red LAN CLI estilo router.")
        while self.running:
            cmd = input(self.prompt.get_prompt()).strip()
            self.parse_command(cmd)

    def parse_command(self, cmd):
        """Analiza y ejecuta el comando ingresado por el usuario.

        Usa `self.command_map` para despachar al manejador correspondiente.

        Args:
            cmd (str): Comando completo ingresado.

        Returns:
            None
        """
        parts = cmd.split()
        if not parts:
            return
        cmd_lower = cmd.lower()
        
        if cmd_lower in self.command_map:
            self.command_map[cmd_lower](parts)
            return

        # Try two-word command match
        if len(parts) >= 2:
            key2 = f"{parts[0]} {parts[1]}".lower()
            if key2 in self.command_map:
                self.command_map[key2](parts)
                return

        # Fallback to single-word command match
        key = parts[0].lower()
        handler = self.command_map.get(key)
        if handler:
            handler(parts)
        else:
            print("Comando no reconocido o incompleto.")


    def _handle_quit(self, parts):
        self.running = False
        print("Saliendo del simulador...")

    def _handle_exit(self, parts):
        self.prompt.exit_mode()

    def _handle_enable(self, parts):
        self.prompt.elevate_privilege()

    def _handle_disable(self, parts):
        self.prompt.reset()

    def _handle_configure(self, parts):
        self.prompt.enter_global_config()

    def _handle_hostname(self, parts):
        if len(parts) == 2:
            name = parts[1]
            self.prompt.set_device_name(name)
            if not self.network.find_device(name):
                self.network.add_device(Router(name))

    def _handle_interface(self, parts):
        if len(parts) == 2:
            device = self.network.find_device(self.prompt.device_name)
            if device:
                self.prompt.enter_interface_config(parts[1])
                device.add_interface(parts[1])
            else:
                print(f"Error: El dispositivo '{self.prompt.device_name}' no existe. Usa 'hostname <nombre>' para crearlo primero.")

    def _handle_ip_address(self, parts):
        if len(parts) == 3:
            device = self.network.find_device(self.prompt.device_name)
            if device:
                iface = device.get_interface(self.prompt.interface)
                if iface:
                    iface.ip_address = parts[2]
                else:
                    print(f"Error: La interfaz '{self.prompt.interface}' no existe en el dispositivo '{self.prompt.device_name}'.")
            else:
                print(f"Error: El dispositivo '{self.prompt.device_name}' no existe.")

    def _handle_no_shutdown(self, parts):
        device = self.network.find_device(self.prompt.device_name)
        if device:
            iface = device.get_interface(self.prompt.interface)
            if iface:
                iface.status = 'up'
            else:
                print(f"Error: La interfaz '{self.prompt.interface}' no existe en el dispositivo '{self.prompt.device_name}'.")
        else:
            print(f"Error: El dispositivo '{self.prompt.device_name}' no existe.")

    def _handle_shutdown(self, parts):
        device = self.network.find_device(self.prompt.device_name)
        if device:
            iface = device.get_interface(self.prompt.interface)
            if iface:
                iface.status = 'down'
            else:
                print(f"Error: La interfaz '{self.prompt.interface}' no existe en el dispositivo '{self.prompt.device_name}'.")
        else:
            print(f"Error: El dispositivo '{self.prompt.device_name}' no existe.")

    def _handle_connect(self, parts):
        if len(parts) == 5:
            try:
                self.network.connect(parts[1], parts[2], parts[3], parts[4])
            except ValueError:
                print("Device not found.")
        else:
            print("Usage: connect <source_device> <source_interface> <destination_device> <destination_interface>")

    def _handle_disconnect(self, parts):
        if len(parts) == 5:
            try:
                self.network.disconnect(parts[1], parts[2], parts[3], parts[4])
            except ValueError:
                print("Device not found.")
        else:
            print("Usage: disconnect <source_device> <source_interface> <destination_device> <destination_interface>")

    def _handle_list_devices(self, parts):
        self.network.list_devices()

    def _handle_set_device_status(self, parts):
        if len(parts) == 3:
            self.network.set_device_status(parts[1], parts[2])

    def _handle_show_history(self, parts):
        if len(parts) == 3:
            self.network.show_device_history(parts[2])

    def _handle_show_statistics(self, parts):
        self.network.show_statistics(self.statistics)

    def _handle_tick(self, parts):
        # Process network with statistics tracking
        self.network.process_network(self.statistics)

    def _find_device_by_ip(self, src_ip):
        current = self.network.devices.head
        while current:
            dev = current.data
            iface_node = dev.interfaces.head
            while iface_node:
                if iface_node.data.ip_address == src_ip:
                    return dev, iface_node.data.name
                iface_node = iface_node.next
            current = current.next
        return None, None

    def _handle_send(self, parts):
        if len(parts) >= 5:
            src_ip = parts[1]
            dest_ip = parts[2]
            message = ' '.join(parts[3:-1])
            try:
                ttl = int(parts[-1])
            except ValueError:
                print("TTL inválido")
                return

            dev, iface_name = self._find_device_by_ip(src_ip)
            if dev and iface_name:
                self.network.send_packet(dev.name, iface_name, dest_ip, message, ttl)
                # Log packet sent for statistics
                self.statistics.log_sent()
                print("Message queued for delivery.")
            else:
                print("No se encontró el dispositivo o interfaz con esa IP.")

    def _handle_save(self, parts):
        """
        Guarda el estado de la red en un archivo de configuración.

        Sintaxis: save running-config [<filename>]
        """
        if len(parts) >= 2 and parts[1] == 'running-config':
            filename = parts[2] if len(parts) >= 3 else 'running-config.json'
            ConfigManager.save_running_config(self.network, filename)
            print(f"Configuration saved to {filename}")
        else:
            print("Uso: save running-config [<filename>]")

    def _handle_load(self, parts):
        """
        Carga el estado de la red desde un archivo de configuración.

        Sintaxis: load config <filename>
        """
        # Sintaxis: load config [<filename>]
        if len(parts) >= 2 and parts[1] == 'config':
            filename = parts[2] if len(parts) >= 3 else 'running-config.json'
            ConfigManager.load_config(self.network, filename)
            print("Configuration loaded successfully.")
            print("Devices and connections restored.")
        else:
            print("Uso: load config [<filename>]")

    def _handle_show_interfaces(self, parts):
        if len(parts) == 3:
            self.network.show_interfaces(parts[2])
        else:
            print("Usage: show interfaces <device_name>")
    def _handle_show_queue(self, parts):
        if len(parts) == 3:
            self.network.show_queue(parts[2])
        else:
            print("Usage: show queue <device_name>")
    def _handle_show_connections(self, parts):
        if len(parts) == 3:
            self.network.show_connections(parts[2])
        else:
            print("Usage: show connections <device_name>")
