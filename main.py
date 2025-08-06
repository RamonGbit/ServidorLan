"""Punto de entrada del simulador de red LAN CLI.

Este módulo contiene la función main para inicializar y ejecutar la CLI del simulador.
"""

from Cli.Cli import CLI
from Network.Network import Network
from Persistence.ConfigManager import ConfigManager

def main():
    """Inicializa y ejecuta el simulador de red LAN.

    Carga la configuración y lanza la interfaz de línea de comandos (CLI).

    Raises:
        Exception: Si ocurre un error al cargar la configuración.
    """
    network = Network()
    try:
        ConfigManager.load_config(network, "running-config.json")
        print("Configuración cargada desde running-config.json")
    except Exception:
        print("No se encontró configuración predeterminada; iniciando con una red vacía.")
    cli = CLI()
    cli.network = network
    cli.run()

main()
