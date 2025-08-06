"""Módulo datastructures.linkedlist: implementación simple de lista enlazada sin usar estructuras nativas de Python."""

from DataStructures.Node import Node

class LinkedList:
    """Lista enlazada simple.

    Permite agregar, eliminar y buscar elementos mediante nodos enlazados.
    """
    def __init__(self):
        """Inicializa una lista enlazada vacía."""
        self.head = None
        self.size = 0

    def append(self, data):
        """
        Agrega un elemento al final de la lista.

        Args:
            data: Elemento a agregar.
        """
        node = Node(data)
        if not self.head:
            self.head = node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = node
        self.size += 1

    def remove(self, data):
        """
        Elimina la primera ocurrencia del elemento en la lista.

        Args:
            data: Elemento a eliminar.

        Returns:
            bool: True si se eliminó; False si no se encontró.
        """
        prev = None
        current = self.head
        while current:
            if current.data == data:
                if prev:
                    prev.next = current.next
                else:
                    self.head = current.next
                self.size -= 1
                return True
            prev = current
            current = current.next
        return False

    def find(self, data):
        """
        Busca y retorna el nodo que contiene el elemento especificado.

        Args:
            data: Elemento a buscar.

        Returns:
            Node or None: Nodo que contiene el elemento, o None si no existe.
        """
        current = self.head
        while current:
            if current.data == data:
                return current
            current = current.next
        return None

    def mostrar_elementos(self):
        """
        Imprime todos los elementos de la lista enlazada en orden.
        """
        actual = self.head
        while actual:
            print(actual.data)
            actual = actual.next

    def __len__(self):
        """Retorna el número de elementos en la lista."""
        return self.size
