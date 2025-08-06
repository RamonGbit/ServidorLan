"""Módulo datastructures.queue: implementación de una cola enlazada FIFO sin usar estructuras nativas de Python."""

from DataStructures.Node import Node


class Queue:
    """Estructura FIFO de cola enlazada."""
    def __init__(self):
        """Inicializa una cola vacía."""
        self.front = None
        self.rear = None
        self.size = 0

    def enqueue(self, item):
        """
        Agrega un elemento al final de la cola.

        Args:
            item: Elemento a encolar.
        """
        node = Node(item)
        if not self.rear:
            self.front = node
            self.rear = node
        else:
            self.rear.next = node
            self.rear = node
        self.size += 1

    def dequeue(self):
        """
        Elimina y retorna el elemento al frente de la cola.

        Returns:
            El elemento desencolado.

        Raises:
            IndexError: Si la cola está vacía.
        """
        if self.is_empty():
            raise IndexError("La cola está vacía")
        data = self.front.data
        self.front = self.front.next
        if not self.front:
            self.rear = None
        self.size -= 1
        return data

    def is_empty(self):
        """
        Verifica si la cola está vacía.

        Returns:
            bool: True si la cola no contiene elementos, False en caso contrario.
        """
        return self.front is None

    def peek(self):
        """
        Obtiene el elemento al frente sin eliminarlo de la cola.

        Returns:
            El elemento al frente o None si la cola está vacía.
        """
        if self.is_empty():
            return None
        return self.front.data

    def __len__(self):
        """Retorna el número de elementos en la cola."""
        return self.size
