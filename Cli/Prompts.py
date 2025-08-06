"""Módulo prompts.

Proporciona el gestor de modos y prompt dinámico para la CLI del simulador de red LAN.
"""

class PromptManager:
    """Administra modos y prompt dinámico en la CLI.

    Attributes:
        device_name (str): Nombre del dispositivo en el prompt.
        mode (str): Modo actual ('user', 'privileged', 'global_config', 'interface_config').
        interface (str | None): Nombre de la interfaz en modo de configuración.
    """
    USER_MODE = 'user'
    PRIVILEGED_MODE = 'privileged'
    GLOBAL_CONFIG_MODE = 'global_config'
    INTERFACE_CONFIG_MODE = 'interface_config'

    def __init__(self, device_name='Device'):
        """Inicializa el gestor de prompt.

        Args:
            device_name (str): Nombre inicial del dispositivo.
        """
        self.device_name = device_name
        self.mode = self.USER_MODE
        self.interface = None

    def set_device_name(self, name):
        """
        Actualiza el nombre del dispositivo en el prompt.

        Args:
            name (str): Nuevo nombre sin espacios ni vacío.

        Raises:
            ValueError: Si `name` no es válido.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("El nombre no puede estar vacío.")
        if ' ' in name:
            raise ValueError("El nombre no puede contener espacios.")
        self.device_name = name.strip()

    def set_mode(self, mode, interface=None):
        """
        Establece el modo de operación del prompt.

        Args:
            mode (str): Modo a establecer.
            interface (str, optional): Nombre de interfaz si `mode` es INTERFACE_CONFIG_MODE.

        Raises:
            ValueError: Si `mode` o `interface` no son válidos.
        """
        valid = [self.USER_MODE, self.PRIVILEGED_MODE, self.GLOBAL_CONFIG_MODE, self.INTERFACE_CONFIG_MODE]
        if mode not in valid:
            raise ValueError(f"Modo inválido: {mode}")
        if mode == self.INTERFACE_CONFIG_MODE and (not interface or not isinstance(interface, str)):
            raise ValueError("Se requiere un nombre de interfaz válido.")
        self.mode = mode
        self.interface = interface

    def get_prompt(self):
        """
        Construye la cadena de prompt según el modo actual.

        Returns:
            str: Prompt formateado con nombre, modo e interfaz.
        """
        if self.mode == self.USER_MODE:
            return f"{self.device_name}> "
        if self.mode == self.PRIVILEGED_MODE:
            return f"{self.device_name}# "
        if self.mode == self.GLOBAL_CONFIG_MODE:
            return f"{self.device_name}(config)# "
        if self.mode == self.INTERFACE_CONFIG_MODE and self.interface:
            return f"{self.device_name}(config-if)# "
        return f"{self.device_name}> "

    def elevate_privilege(self):
        """
        Cambia al modo privilegiado (Device#).
        """
        self.set_mode(self.PRIVILEGED_MODE)

    def enter_global_config(self):
        """
        Cambia al modo de configuración global (Device(config)#).
        """
        self.set_mode(self.GLOBAL_CONFIG_MODE)

    def enter_interface_config(self, interface_name):
        """
        Cambia al modo de configuración de la interfaz especificada.

        Args:
            interface_name (str): Nombre de la interfaz a configurar.

        Raises:
            ValueError: Si `interface_name` es inválido.
        """
        if not isinstance(interface_name, str) or not interface_name.strip():
            raise ValueError("El nombre de la interfaz no puede estar vacío.")
        self.set_mode(self.INTERFACE_CONFIG_MODE, interface_name.strip())

    def exit_mode(self):
        """
        Regresa al modo anterior en la jerarquía de configuración.
        """
        if self.mode == self.INTERFACE_CONFIG_MODE:
            self.set_mode(self.GLOBAL_CONFIG_MODE)
        elif self.mode == self.GLOBAL_CONFIG_MODE:
            self.set_mode(self.PRIVILEGED_MODE)
        elif self.mode == self.PRIVILEGED_MODE:
            self.set_mode(self.USER_MODE)

    def reset(self):
        """
        Restablece el modo al usuario (Device>).
        """
        self.set_mode(self.USER_MODE)
