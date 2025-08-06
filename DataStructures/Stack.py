"""Módulo datastructures.stack: implementación de una pila enlazada LIFO sin usar estructuras nativas de Python."""

from DataStructures.Node import Node


class Stack:
    """Estructura de pila LIFO basada en nodos enlazados."""
    def __init__(self):
        """Inicializa una pila vacía."""
        self.top = None
        self.size = 0

    def push(self, item):
        """
        Agrega un elemento a la cima de la pila.

        Args:
            item: Elemento a apilar.
        """
        node = Node(item)
        node.next = self.top
        self.top = node
        self.size += 1

    def pop(self):
        """
        Elimina y retorna el elemento en la cima de la pila.

        Returns:
            El elemento desapilado.

        Raises:
            IndexError: Si la pila está vacía.
        """
        if self.is_empty():
            raise IndexError("La pila está vacía")
        data = self.top.data
        self.top = self.top.next
        self.size -= 1
        return data

    def peek(self):
        """
        Retorna el elemento en la cima sin modificar la pila.

        Returns:
            Elemento superior o None si la pila está vacía.
        """
        if self.is_empty():
            return None
        return self.top.data

    def is_empty(self):
        """
        Verifica si la pila está vacía.

        Returns:
            bool: True si la pila no contiene elementos, False en caso contrario.
        """
        return self.top is None

    def __len__(self):
        """Retorna el número de elementos actualmente en la pila."""
        return self.size
