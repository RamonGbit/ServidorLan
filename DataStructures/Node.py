"""Módulo datastructures.node: define la clase Node para nodos en estructuras enlazadas."""

class Node:
    """Nodo básico para estructuras enlazadas (listas, pilas, colas)."""
    def __init__(self, data):
        """
        Inicializa un nodo con el dato proporcionado.

        Args:
            data: Valor almacenado en el nodo.
        """
        self.data = data
        self.next = None
