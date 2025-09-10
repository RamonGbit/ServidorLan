
"""
Módulo de registro de errores para el proyecto ServidorLan.

Proporciona una cola de errores y funciones para registrar y consultar errores de manera centralizada.
Documentación en formato Google.
"""

import datetime


class ErrorLogNode:
    """Nodo de la cola de errores.

    Attributes:
        timestamp (str): Fecha y hora del error.
        error_type (str): Tipo o categoría del error.
        message (str): Mensaje descriptivo del error.
        command (str, optional): Comando asociado al error, si aplica.
        next (ErrorLogNode): Referencia al siguiente nodo en la cola.
    """
    def __init__(self, timestamp, error_type, message, command=None):
        """Inicializa un nodo de error.

        Args:
            timestamp (str): Fecha y hora del error.
            error_type (str): Tipo o categoría del error.
            message (str): Mensaje descriptivo del error.
            command (str, optional): Comando asociado al error.
        """
        self.timestamp = timestamp
        self.error_type = error_type
        self.message = message
        self.command = command
        self.next = None

    def __str__(self):
        """Devuelve una representación legible del error."""
        cmd = f" | Command: {self.command}" if self.command else ""
        return f"[{self.timestamp}] {self.error_type}: {self.message}{cmd}"


class ErrorLogQueue:
    """Cola de errores para almacenar eventos de error.

    Métodos para encolar, desencolar y consultar errores.
    """
    def __init__(self):
        """Inicializa la cola de errores vacía."""
        self.head = None
        self.tail = None
        self.size = 0

    def enqueue(self, error_type, message, command=None):
        """Agrega un error a la cola.

        Args:
            error_type (str): Tipo o categoría del error.
            message (str): Mensaje descriptivo del error.
            command (str, optional): Comando asociado al error.
        """
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        node = ErrorLogNode(timestamp, error_type, message, command)
        if not self.head:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1

    def dequeue(self):
        """Elimina y retorna el error más antiguo de la cola.

        Returns:
            ErrorLogNode or None: Nodo de error o None si la cola está vacía.
        """
        if not self.head:
            return None
        node = self.head
        self.head = self.head.next
        if not self.head:
            self.tail = None
        self.size -= 1
        return node

    def get_all(self, n=None):
        """Obtiene una lista de los errores almacenados.

        Args:
            n (int, optional): Máximo número de errores a retornar. Si es None, retorna todos.

        Returns:
            list[ErrorLogNode]: Lista de nodos de error.
        """
        result = []
        current = self.head
        while current and (n is None or len(result) < n):
            result.append(current)
            current = current.next
        return result

    def is_empty(self):
        """Indica si la cola está vacía.

        Returns:
            bool: True si está vacía, False en caso contrario.
        """
        return self.size == 0


# Instancia singleton de la cola de errores para todo el proyecto
error_log_queue = ErrorLogQueue()


def log_error(error_type, message, command=None):
    """Registra un error en la cola global de errores.

    Args:
        error_type (str): Tipo o categoría del error.
        message (str): Mensaje descriptivo del error.
        command (str, optional): Comando asociado al error.
    """
    error_log_queue.enqueue(error_type, message, command)


def get_error_log(n=None):
    """Obtiene los errores almacenados en la cola global.

    Args:
        n (int, optional): Máximo número de errores a retornar. Si es None, retorna todos.

    Returns:
        list[ErrorLogNode]: Lista de nodos de error.
    """
    return error_log_queue.get_all(n)
