"""Módulo cli.

Interfaz de línea de comandos para el simulador de red LAN estilo router.
"""

# CLI principal y parser de comandos

from Network.Network import Network
from Network.Device import Router, Switch, Host, Firewall
from Statistics.Statistics import Statistics
from Cli.Prompts import PromptManager
from Persistence.ConfigManager import ConfigManager

from ErrorLog import log_error, get_error_log
from Persistence.BTreeIndex import BTreeIndex
from PolicyTrie.PolicyTrie import PolicyTrie

class CLI:
    """Interfaz de línea de comandos para el simulador de red LAN estilo router.

    Aporta comandos para gestionar dispositivos, rutas, políticas, snapshots y estadísticas de la red.

    Attributes:
        network (Network): Gestor de topología de red.
        statistics (Statistics): Estadísticas de la red.
        prompt (PromptManager): Gestor del prompt interactivo.
        running (bool): Indicador de ciclo de ejecución.
        command_map (dict): Mapa de comandos a métodos manejadores.
        btree_index (BTreeIndex): Índice B-Tree para snapshots.
        snapshot_counter (int): Contador para snapshots.
        policy_trie (PolicyTrie): Trie de políticas de red.
    """
    def __init__(self):
        """Inicializa la CLI y sus componentes principales.

        Crea instancias de red, estadísticas, prompt, índice B-Tree y trie de políticas.
        """
        self.network = Network()
        self.statistics = Statistics()
        self.prompt = PromptManager()
        self.running = True

        self.btree_index = BTreeIndex(order=4)
        self.snapshot_counter = 16
        self.policy_trie = PolicyTrie()
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
            'show error-log': self._handle_show_error_log,
            # Comandos de routing AVL
            'ip route': self._handle_ip_route,
            'show ip route': self._handle_show_ip_route,
            'show route avl-stats': self._handle_show_route_avl_stats,
            'show ip route-tree': self._handle_show_ip_route_tree,
            'save snapshot': self._handle_save_snapshot,
            'show snapshots': self._handle_show_snapshots,
            'btree stats': self._handle_btree_stats,
            # Comandos de políticas y trie
            'policy set': self._handle_policy_set,
            'policy unset': self._handle_policy_unset,
            'show ip prefix-tree': self._handle_show_ip_prefix_tree,
        }

    def _handle_policy_set(self, parts):
        # policy set <prefix> <mask> ttl-min <N>
        # policy set <prefix> <mask> block
        if len(parts) == 6 and parts[4] == 'ttl-min':
            prefix = parts[2]
            mask = parts[3]
            try:
                ttl = int(parts[5])
            except ValueError:
                print("TTL debe ser un número entero.")
                return
            self.policy_trie.set_policy(prefix, mask, {'ttl-min': ttl})
            print(f"Política ttl-min={ttl} aplicada a {prefix}/{mask}")
        elif len(parts) == 5 and parts[4] == 'block':
            prefix = parts[2]
            mask = parts[3]
            self.policy_trie.set_policy(prefix, mask, {'block': True})
            print(f"Política de bloqueo aplicada a {prefix}/{mask}")
        else:
            print("Uso: policy set <prefix> <mask> ttl-min <N>  o  policy set <prefix> <mask> block")

    def _handle_policy_unset(self, parts):
        # policy unset <prefix> <mask>
        if len(parts) == 4:
            prefix = parts[2]
            mask = parts[3]
            ok = self.policy_trie.unset_policy(prefix, mask)
            if ok:
                print(f"Política eliminada de {prefix}/{mask}")
            else:
                print(f"No se encontró política para {prefix}/{mask}")
        else:
            print("Uso: policy unset <prefix> <mask>")

    def _handle_show_ip_prefix_tree(self, parts):
        print("Trie de prefijos y políticas:")
        self.policy_trie.print_trie()

    def _handle_policy_set(self, parts):
        # policy set <prefix> <mask> ttl-min <N>
        # policy set <prefix> <mask> block
        if len(parts) == 6 and parts[4] == 'ttl-min':
            prefix = parts[2]
            mask = parts[3]
            try:
                ttl = int(parts[5])
            except ValueError:
                print("TTL debe ser un número entero.")
                return
            self.policy_trie.set_policy(prefix, mask, {'ttl-min': ttl})
            print(f"Política ttl-min={ttl} aplicada a {prefix}/{mask}")
        elif len(parts) == 5 and parts[4] == 'block':
            prefix = parts[2]
            mask = parts[3]
            self.policy_trie.set_policy(prefix, mask, {'block': True})
            print(f"Política de bloqueo aplicada a {prefix}/{mask}")
        else:
            print("Uso: policy set <prefix> <mask> ttl-min <N>  o  policy set <prefix> <mask> block")

    def _handle_policy_unset(self, parts):
        # policy unset <prefix> <mask>
        if len(parts) == 4:
            prefix = parts[2]
            mask = parts[3]
            ok = self.policy_trie.unset_policy(prefix, mask)
            if ok:
                print(f"Política eliminada de {prefix}/{mask}")
            else:
                print(f"No se encontró política para {prefix}/{mask}")
        else:
            print("Uso: policy unset <prefix> <mask>")

    def _handle_show_ip_prefix_tree(self, parts):
        print("Trie de prefijos y políticas:")
        self.policy_trie.print_trie()
    # ...existing code...

    def _handle_save_snapshot(self, parts):
        # save snapshot <key>
        if len(parts) == 3:
            key = parts[2]
            filename = f"snap_{self.snapshot_counter:05d}.cfg"
            self.snapshot_counter += 1
            # Aquí se simula guardar el archivo, en la práctica se usaría ConfigManager
            self.btree_index.insert(key, filename)
            print(f"[OK] snapshot {key} -> file: {filename} (indexed)")
        else:
            print("Uso: save snapshot <key>")

    def _handle_show_snapshots(self, parts):
        # show snapshots
        entries = self.btree_index.inorder()
        if not entries:
            print("No hay snapshots indexados.")
        else:
            for k, v in entries:
                print(f"{k} -> {v}")

    def _handle_btree_stats(self, parts):
        stats = self.btree_index.get_stats()
        print(f"order={stats['order']} height={stats['height']} nodes={stats['nodes']} splits={stats['splits']} merges={stats['merges']}")
    # --- Comandos de Routing AVL ---
    def _handle_ip_route(self, parts):
        # Sintaxis: ip route add <prefix> <mask> via <next-hop> [metric N]
        if len(parts) >= 7 and parts[2] == 'add' and parts[5] == 'via':
            prefix = parts[3]
            mask = parts[4]
            next_hop = parts[6]
            metric = int(parts[8]) if len(parts) >= 9 and parts[7] == 'metric' else 1
            router = self.network.find_device(self.prompt.device_name)
            if router and hasattr(router, 'route_table'):
                router.route_table.insert(prefix, mask, next_hop, metric)
                router.route_table.print_tree()
                print(f"Ruta agregada: {prefix}/{mask} via {next_hop} metric {metric}")
            else:
                print("No hay router seleccionado o no soporta rutas AVL.")
        # Sintaxis: ip route del <prefix> <mask>
        elif len(parts) == 5 and parts[2] == 'del':
            prefix = parts[3]
            mask = parts[4]
            router = self.network.find_device(self.prompt.device_name)
            if router and hasattr(router, 'route_table'):
                removed = router.route_table.delete(prefix, mask)
                if removed:
                    print(f"Ruta eliminada: {prefix}/{mask}")
                else:
                    print(f"No se encontró la ruta {prefix}/{mask}")
            else:
                print("No hay router seleccionado o no soporta rutas AVL.")
        else:
            print("Uso: ip route add <prefix> <mask> via <next-hop> [metric N]  o  ip route del <prefix> <mask>")

    def _handle_show_ip_route(self, parts):
        router = self.network.find_device(self.prompt.device_name)
        if router and hasattr(router, 'route_table'):
            routes = router.route_table.inorder()
            if not routes:
                print("Tabla de rutas vacía.")
            else:
                print("Rutas registradas:")
                for prefix, mask, next_hop, metric in routes:
                    print(f"{prefix}/{mask} via {next_hop} metric {metric}")
                print("\nEstructura AVL de la tabla de rutas:")
                router.route_table.print_tree()
        else:
            print("No hay router seleccionado o no soporta rutas AVL.")

    def _handle_show_route_avl_stats(self, parts):
        router = self.network.find_device(self.prompt.device_name)
        if router and hasattr(router, 'route_table'):
            stats = router.route_table.get_stats()
            print(f"nodes={stats['nodes']} height={stats['height']} rotations: LL={stats['LL']} LR={stats['LR']} RL={stats['RL']} RR={stats['RR']}")
        else:
            print("No hay router seleccionado o no soporta rutas AVL.")

    def _handle_show_ip_route_tree(self, parts):
        router = self.network.find_device(self.prompt.device_name)
        if router and hasattr(router, 'route_table'):
            router.route_table.print_tree()
        else:
            print("No hay router seleccionado o no soporta rutas AVL.")

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
            cmd (str): Comando completo ingresado por el usuario.

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
            try:
                handler(parts)
            except Exception as e:
                print(f"Error ejecutando comando: {e}")
                log_error(
                    error_type="CommandException",
                    message=str(e),
                    command=cmd
                )
        else:
            print("Comando no reconocido o incompleto.")
            log_error(
                error_type="CommandError",
                message="Unrecognized or incomplete command.",
                command=cmd
            )
    def _handle_show_error_log(self, parts):
        """Muestra el log de errores almacenados.

        Args:
            parts (list): Lista de partes del comando.
        """
        n = None
        if len(parts) == 3:
            try:
                n = int(parts[2])
            except ValueError:
                print("Cantidad inválida, mostrando todos los errores.")
                n = None
        errors = get_error_log(n)
        if not errors:
            print("No errors logged.")
            return
        for err in errors:
            print(err)


    def _handle_quit(self, parts):
        """Finaliza la ejecución de la CLI.

        Args:
            parts (list): Lista de partes del comando.
        """
        self.running = False
        print("Saliendo del simulador...")

    def _handle_exit(self, parts):
        """Sale del modo actual del prompt.

        Args:
            parts (list): Lista de partes del comando.
        """
        self.prompt.exit_mode()

    def _handle_enable(self, parts):
        """Eleva el privilegio del prompt.

        Args:
            parts (list): Lista de partes del comando.
        """
        self.prompt.elevate_privilege()

    def _handle_disable(self, parts):
        """Reinicia el prompt al modo usuario.

        Args:
            parts (list): Lista de partes del comando.
        """
        self.prompt.reset()

    def _handle_configure(self, parts):
        """Entra en modo de configuración global.

        Args:
            parts (list): Lista de partes del comando.
        """
        self.prompt.enter_global_config()

    def _handle_hostname(self, parts):
        """Cambia el nombre del dispositivo actual o lo crea si no existe.

        Args:
            parts (list): Lista de partes del comando.
        """
        if len(parts) == 2:
            name = parts[1]
            try:
                self.prompt.set_device_name(name)
            except Exception as e:
                print(f"Error: {e}")
                log_error("SyntaxError", str(e), f"hostname {name}")
                return
            if not self.network.find_device(name):
                self.network.add_device(Router(name))

    def _handle_interface(self, parts):
        """Entra en modo de configuración de interfaz y la crea si es necesario.

        Args:
            parts (list): Lista de partes del comando.
        """
        if len(parts) == 2:
            device = self.network.find_device(self.prompt.device_name)
            if device:
                try:
                    self.prompt.enter_interface_config(parts[1])
                except Exception as e:
                    print(f"Error: {e}")
                    log_error("SyntaxError", str(e), f"interface {parts[1]}")
                    return
                device.add_interface(parts[1])
            else:
                print(f"Error: El dispositivo '{self.prompt.device_name}' no existe. Usa 'hostname <nombre>' para crearlo primero.")
                log_error("ConnectionError", f"Dispositivo '{self.prompt.device_name}' no existe", f"interface {parts[1]}")

    def _handle_ip_address(self, parts):
        """Asigna una dirección IP a la interfaz seleccionada del dispositivo actual.

        Args:
            parts (list): Lista de partes del comando.
        """
        if len(parts) == 3:
            device = self.network.find_device(self.prompt.device_name)
            if device:
                iface = device.get_interface(self.prompt.interface)
                if iface:
                    iface.ip_address = parts[2]
                else:
                    print(f"Error: La interfaz '{self.prompt.interface}' no existe en el dispositivo '{self.prompt.device_name}'.")
                    log_error("ConnectionError", f"Interfaz '{self.prompt.interface}' no existe en '{self.prompt.device_name}'", f"ip address {parts[2]}")
            else:
                print(f"Error: El dispositivo '{self.prompt.device_name}' no existe.")
                log_error("ConnectionError", f"Dispositivo '{self.prompt.device_name}' no existe", f"ip address {parts[2]}")

    def _handle_no_shutdown(self, parts):
        """Activa la interfaz seleccionada del dispositivo actual.

        Args:
            parts (list): Lista de partes del comando.
        """
        device = self.network.find_device(self.prompt.device_name)
        if device:
            iface = device.get_interface(self.prompt.interface)
            if iface:
                iface.status = 'up'
            else:
                print(f"Error: La interfaz '{self.prompt.interface}' no existe en el dispositivo '{self.prompt.device_name}'.")
                log_error("ConnectionError", f"Interfaz '{self.prompt.interface}' no existe en '{self.prompt.device_name}'", "no shutdown")
        else:
            print(f"Error: El dispositivo '{self.prompt.device_name}' no existe.")
            log_error("ConnectionError", f"Dispositivo '{self.prompt.device_name}' no existe", "no shutdown")

    def _handle_shutdown(self, parts):
        """Desactiva la interfaz seleccionada del dispositivo actual.

        Args:
            parts (list): Lista de partes del comando.
        """
        device = self.network.find_device(self.prompt.device_name)
        if device:
            iface = device.get_interface(self.prompt.interface)
            if iface:
                iface.status = 'down'
            else:
                print(f"Error: La interfaz '{self.prompt.interface}' no existe en el dispositivo '{self.prompt.device_name}'.")
                log_error("ConnectionError", f"Interfaz '{self.prompt.interface}' no existe en '{self.prompt.device_name}'", "shutdown")
        else:
            print(f"Error: El dispositivo '{self.prompt.device_name}' no existe.")
            log_error("ConnectionError", f"Dispositivo '{self.prompt.device_name}' no existe", "shutdown")

    def _handle_connect(self, parts):
        """Conecta dos interfaces de dispositivos de red.

        Args:
            parts (list): Lista de partes del comando.
        """
        if len(parts) == 5:
            try:
                self.network.connect(parts[1], parts[2], parts[3], parts[4])
            except ValueError as e:
                print("Device not found.")
                log_error("ConnectionError", str(e), f"connect {' '.join(parts[1:])}")
        else:
            print("Usage: connect <source_device> <source_interface> <destination_device> <destination_interface>")
            log_error("SyntaxError", "Uso incorrecto de connect", f"connect {' '.join(parts[1:])}")

    def _handle_disconnect(self, parts):
        """Desconecta dos interfaces de dispositivos de red.

        Args:
            parts (list): Lista de partes del comando.
        """
        if len(parts) == 5:
            try:
                self.network.disconnect(parts[1], parts[2], parts[3], parts[4])
            except ValueError as e:
                print("Device not found.")
                log_error("ConnectionError", str(e), f"disconnect {' '.join(parts[1:])}")
        else:
            print("Usage: disconnect <source_device> <source_interface> <destination_device> <destination_interface>")
            log_error("SyntaxError", "Uso incorrecto de disconnect", f"disconnect {' '.join(parts[1:])}")

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
            # Si se da un key, úsalo, si no, usa un timestamp
            import datetime
            key = parts[2] if len(parts) >= 3 else datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"snap_{self.snapshot_counter:05d}.cfg"
            self.snapshot_counter += 1
            ConfigManager.save_running_config(self.network, filename)
            self.btree_index.insert(key, filename)
            print(f"[OK] running-config guardado como {filename} e indexado con clave '{key}'")
        else:
            print("Uso: save running-config [<key>]")

    def _handle_load(self, parts):
        """
        Carga el estado de la red desde un archivo de configuración.

        Sintaxis: load config <filename>
        """
        # Sintaxis: load config [<filename>]
        if len(parts) >= 3 and parts[1] == 'config':
            key = parts[2]
            filename = self.btree_index.search(key)
            if filename:
                ConfigManager.load_config(self.network, filename)
                print(f"[OK] Configuración '{key}' cargada desde archivo {filename}.")
            else:
                print(f"No se encontró snapshot con clave '{key}' en el índice.")
        else:
            print("Uso: load config <key>")

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
                try:
                    self.network.show_connections(parts[2])
                except ValueError as e:
                    print(e)
        else:
            print("Usage: show connections <device_name>")
