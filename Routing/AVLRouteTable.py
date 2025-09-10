

"""
Módulo de Tabla de Rutas Balanceada con AVL para routers.

Implementa una tabla de rutas basada en árbol AVL, con integración de log de errores.
Documentación en formato Google.
"""

# Integración del sistema de log de errores
from ErrorLog import log_error


class AVLNode:
    """Nodo de un árbol AVL para rutas de red.

    Attributes:
        prefix (str): Prefijo de red (IP).
        mask (str): Máscara de red.
        next_hop (str): Siguiente salto.
        metric (int): Métrica de la ruta.
        left (AVLNode): Hijo izquierdo.
        right (AVLNode): Hijo derecho.
        height (int): Altura del nodo.
    """
    def __init__(self, prefix, mask, next_hop, metric):
        """Inicializa un nodo AVL.

        Args:
            prefix (str): Prefijo de red (IP).
            mask (str): Máscara de red.
            next_hop (str): Siguiente salto.
            metric (int): Métrica de la ruta.
        """
        self.prefix = prefix
        self.mask = mask
        self.next_hop = next_hop
        self.metric = metric
        self.left = None
        self.right = None
        self.height = 1


class AVLRouteTable:
    """Tabla de rutas basada en árbol AVL para routers.

    Permite insertar, borrar, buscar y visualizar rutas, manteniendo balance y estadísticas.

    Attributes:
        root (AVLNode): Nodo raíz del árbol AVL.
        stats (dict): Estadísticas del árbol (nodos, altura, rotaciones).
    """
    def __init__(self):
        """Inicializa la tabla de rutas AVL y sus estadísticas."""
        self.root = None
        self.stats = {'nodes': 0, 'height': 0, 'LL': 0, 'LR': 0, 'RL': 0, 'RR': 0}


    def insert(self, prefix, mask, next_hop, metric, command=None):
        """Inserta una ruta en el árbol AVL.

        Args:
            prefix (str): Prefijo de red (IP).
            mask (str): Máscara de red.
            next_hop (str): Siguiente salto.
            metric (int): Métrica de la ruta.
            command (str, optional): Comando asociado para log de error.
        """
        try:
            if not self._valid_prefix_mask(prefix, mask):
                log_error("InsertError", f"Prefijo o máscara inválida: {prefix}/{mask}", command)
                return
            self.root, rotation = self._insert(self.root, prefix, mask, next_hop, metric)
            self.stats['nodes'] = self._count_nodes(self.root)
            self.stats['height'] = self._get_height(self.root)
            if rotation:
                self.stats[rotation] += 1
        except Exception as e:
            log_error("InsertError", f"Error insertando ruta {prefix}/{mask}: {e}", command)

    def _insert(self, node, prefix, mask, next_hop, metric):
        if not node:
            return AVLNode(prefix, mask, next_hop, metric), None
        if (prefix, mask) < (node.prefix, node.mask):
            node.left, rot = self._insert(node.left, prefix, mask, next_hop, metric)
        elif (prefix, mask) > (node.prefix, node.mask):
            node.right, rot = self._insert(node.right, prefix, mask, next_hop, metric)
        else:
            node.next_hop = next_hop
            node.metric = metric
            return node, None
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)
        # Rotaciones AVL
        if balance > 1:
            if (prefix, mask) < (node.left.prefix, node.left.mask):
                return self._right_rotate(node), 'LL'
            else:
                node.left = self._left_rotate(node.left)
                return self._right_rotate(node), 'LR'
        if balance < -1:
            if (prefix, mask) > (node.right.prefix, node.right.mask):
                return self._left_rotate(node), 'RR'
            else:
                node.right = self._right_rotate(node.right)
                return self._left_rotate(node), 'RL'
        return node, None


    def delete(self, prefix, mask, command=None):
        """Elimina una ruta del árbol AVL.

        Args:
            prefix (str): Prefijo de red (IP).
            mask (str): Máscara de red.
            command (str, optional): Comando asociado para log de error.

        Returns:
            bool: True si la ruta fue eliminada, False si no se encontró o hubo error.
        """
        try:
            if not self._valid_prefix_mask(prefix, mask):
                log_error("DeleteError", f"Prefijo o máscara inválida: {prefix}/{mask}", command)
                return False
            self.root, deleted = self._delete(self.root, prefix, mask)
            self.stats['nodes'] = self._count_nodes(self.root)
            self.stats['height'] = self._get_height(self.root)
            if not deleted:
                log_error("DeleteError", f"Ruta no encontrada para borrar: {prefix}/{mask}", command)
            return deleted
        except Exception as e:
            log_error("DeleteError", f"Error borrando ruta {prefix}/{mask}: {e}", command)
            return False

    def _delete(self, node, prefix, mask):
        if not node:
            return node, False
        if (prefix, mask) < (node.prefix, node.mask):
            node.left, deleted = self._delete(node.left, prefix, mask)
        elif (prefix, mask) > (node.prefix, node.mask):
            node.right, deleted = self._delete(node.right, prefix, mask)
        else:
            # Nodo encontrado
            deleted = True
            if not node.left:
                return node.right, deleted
            elif not node.right:
                return node.left, deleted
            # Nodo con dos hijos: obtener sucesor
            succ = self._min_value_node(node.right)
            node.prefix, node.mask, node.next_hop, node.metric = succ.prefix, succ.mask, succ.next_hop, succ.metric
            node.right, _ = self._delete(node.right, succ.prefix, succ.mask)
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)
        # Rotaciones AVL tras borrado
        if balance > 1:
            if self._get_balance(node.left) >= 0:
                return self._right_rotate(node), deleted
            else:
                node.left = self._left_rotate(node.left)
                return self._right_rotate(node), deleted
        if balance < -1:
            if self._get_balance(node.right) <= 0:
                return self._left_rotate(node), deleted
            else:
                node.right = self._right_rotate(node.right)
                return self._left_rotate(node), deleted
        return node, deleted

    def _min_value_node(self, node):
        current = node
        while current.left:
            current = current.left
        return current

    def _get_height(self, node):
        return node.height if node else 0

    def _get_balance(self, node):
        return self._get_height(node.left) - self._get_height(node.right) if node else 0

    def _right_rotate(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))
        return x

    def _left_rotate(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = 1 + max(self._get_height(x.left), self._get_height(x.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def _count_nodes(self, node):
        if not node:
            return 0
        return 1 + self._count_nodes(node.left) + self._count_nodes(node.right)


    def find(self, prefix, mask, command=None):
        """Busca una ruta en el árbol AVL.

        Args:
            prefix (str): Prefijo de red (IP).
            mask (str): Máscara de red.
            command (str, optional): Comando asociado para log de error.

        Returns:
            AVLNode or None: Nodo encontrado o None si no existe.
        """
        try:
            if not self._valid_prefix_mask(prefix, mask):
                log_error("FindError", f"Prefijo o máscara inválida: {prefix}/{mask}", command)
                return None
            node = self.root
            while node:
                if (prefix, mask) < (node.prefix, node.mask):
                    node = node.left
                elif (prefix, mask) > (node.prefix, node.mask):
                    node = node.right
                else:
                    return node
            log_error("FindError", f"Ruta no encontrada: {prefix}/{mask}", command)
            return None
        except Exception as e:
            log_error("FindError", f"Error buscando ruta {prefix}/{mask}: {e}", command)
            return None
    def _valid_prefix_mask(self, prefix, mask):
        # Validación simple de IP y máscara (puede mejorarse)
        try:
            parts = prefix.split('.')
            if len(parts) != 4 or not all(0 <= int(p) <= 255 for p in parts):
                return False
            mask_int = int(mask)
            if not (0 <= mask_int <= 32):
                return False
            return True
        except Exception:
            return False

    def inorder(self):
        """Devuelve una lista de todas las rutas en orden.

        Returns:
            list[tuple]: Lista de tuplas (prefix, mask, next_hop, metric).
        """
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append((node.prefix, node.mask, node.next_hop, node.metric))
            self._inorder(node.right, result)

    def print_tree(self, node=None, prefix="", is_left=None):
        """Imprime el árbol AVL de rutas de forma jerárquica.

        Args:
            node (AVLNode, optional): Nodo desde el que imprimir (por defecto la raíz).
            prefix (str, optional): Prefijo visual para la jerarquía.
            is_left (bool, optional): Indica si el nodo es hijo izquierdo.
        """
        if node is None:
            node = self.root
        if node is None:
            return
            
        # Para la raíz
        if prefix == "":
            print(f"[{node.prefix}/{node.mask}]")
            new_prefix = prefix + "|   " if node.left or node.right else prefix + "    "
            if node.left:
                self.print_tree(node.left, new_prefix, True)
            if node.right:
                self.print_tree(node.right, new_prefix, False)
            return
        
        # Para nodos no raíz
        connector = "└── " if not is_left else "├── "
        print(f"{prefix}{connector}[{node.prefix}/{node.mask}]")
        
        # Actualizar el prefijo para los hijos
        extension = "    " if not is_left or (not node.left and not node.right) else "|   "
        new_prefix = prefix + extension
        
        # Imprimir hijos
        if node.left:
            self.print_tree(node.left, new_prefix, True)
        if node.right:
            self.print_tree(node.right, new_prefix, False)

    def get_stats(self):
        """Devuelve una copia de las estadísticas del árbol AVL.

        Returns:
            dict: Estadísticas (nodos, altura, rotaciones).
        """
        return self.stats.copy()