
"""
Módulo PolicyTrie para prefijos IP y políticas jerárquicas (Trie binario).

Implementa un trie binario para gestionar políticas de red asociadas a prefijos IP.
Documentación en formato Google.
"""


class TrieNode:
    """Nodo de un trie binario para prefijos IP y políticas.

    Attributes:
        children (dict): Hijos del nodo (bits '0' y '1').
        policy (dict or None): Política asociada al nodo.
        is_end (bool): Indica si es fin de un prefijo válido.
    """
    def __init__(self):
        """Inicializa un nodo de trie binario."""
        self.children = {}
        self.policy = None  # {'ttl-min': N} o {'block': True}
        self.is_end = False


class PolicyTrie:
    """Trie binario para gestionar políticas jerárquicas de prefijos IP.

    Permite asociar políticas a prefijos y realizar búsquedas de coincidencia más larga.

    Attributes:
        root (TrieNode): Nodo raíz del trie.
    """
    def __init__(self):
        """Inicializa el trie de políticas con un nodo raíz."""
        self.root = TrieNode()

    def _ip_to_bin(self, ip, mask):
        """Convierte una IP y máscara a una cadena binaria según la longitud de la máscara.

        Args:
            ip (str): Dirección IP en formato decimal.
            mask (str): Máscara en formato decimal.

        Returns:
            str: Cadena binaria representando el prefijo.
        """
        from ErrorLog import log_error
        try:
            ip_parts = [int(x) for x in ip.split('.')]
            if len(ip_parts) != 4 or not all(0 <= part < 256 for part in ip_parts):
                raise ValueError("IP inválida")
            ip_bin = ''.join(f'{part:08b}' for part in ip_parts)
            mask_parts = [int(x) for x in mask.split('.')]
            if len(mask_parts) != 4 or not all(0 <= part < 256 for part in mask_parts):
                raise ValueError("Máscara inválida")
            mask_len = sum(bin(int(x)).count('1') for x in mask.split('.'))
            return ip_bin[:mask_len]
        except Exception as e:
            log_error('PolicyTrieError', f'Error en _ip_to_bin: {e}', f'ip={ip} mask={mask}')
            return ''

    def set_policy(self, prefix, mask, policy):
        """Asocia una política a un prefijo/máscara en el trie.

        Args:
            prefix (str): Prefijo de red (IP).
            mask (str): Máscara de red.
            policy (dict): Política a asociar (ej. {'ttl-min': N} o {'block': True}).

        Returns:
            bool: True si se asignó correctamente, False si hubo error.
        """
        from ErrorLog import log_error
        node = self.root
        path = self._ip_to_bin(prefix, mask)
        if not path:
            log_error('PolicyTrieError', 'Prefijo/máscara inválidos en set_policy', f'{prefix}/{mask}')
            return False
        for bit in path:
            if bit not in node.children:
                node.children[bit] = TrieNode()
            node = node.children[bit]
        node.policy = policy
        node.is_end = True
        return True

    def unset_policy(self, prefix, mask):
        """Elimina la política asociada a un prefijo/máscara.

        Args:
            prefix (str): Prefijo de red (IP).
            mask (str): Máscara de red.

        Returns:
            bool: True si se eliminó correctamente, False si hubo error.
        """
        from ErrorLog import log_error
        node = self.root
        path = self._ip_to_bin(prefix, mask)
        if not path:
            log_error('PolicyTrieError', 'Prefijo/máscara inválidos en unset_policy', f'{prefix}/{mask}')
            return False
        for bit in path:
            if bit not in node.children:
                log_error('PolicyTrieError', 'No existe el prefijo/máscara en unset_policy', f'{prefix}/{mask}')
                return False
            node = node.children[bit]
        node.policy = None
        node.is_end = False
        return True

    def get_policy(self, ip):
        """Busca la política más específica (longest-prefix match) para una IP.

        Args:
            ip (str): Dirección IP a consultar.

        Returns:
            dict or None: Política encontrada o None si no hay coincidencia.
        """
        from ErrorLog import log_error
        try:
            node = self.root
            ip_parts = [int(x) for x in ip.split('.')]
            if len(ip_parts) != 4 or not all(0 <= part < 256 for part in ip_parts):
                raise ValueError("IP inválida")
            ip_bin = ''.join(f'{part:08b}' for part in ip_parts)
            policy = None
            for bit in ip_bin:
                if bit in node.children:
                    node = node.children[bit]
                    if node.policy is not None:
                        policy = node.policy
                else:
                    break
            return policy
        except Exception as e:
            log_error('PolicyTrieError', f'Error en get_policy: {e}', f'ip={ip}')
            return None

    def print_trie(self):
        """Imprime el trie de políticas en formato legible por consola."""
        def _print(node, prefix_bin, depth):
            if node.policy is not None:
                ip = '.'.join(str(int(prefix_bin[i:i+8], 2)) for i in range(0, len(prefix_bin), 8))
                mask_len = len(prefix_bin)
                mask = ((1 << mask_len) - 1) << (32 - mask_len)
                mask_str = '.'.join(str((mask >> (24 - 8*i)) & 0xFF) for i in range(4))
                pol_str = f"ttl-min={node.policy['ttl-min']}" if 'ttl-min' in node.policy else 'block'
                print(f"{ip}/{mask_str}   {{{pol_str}}}")
            for bit, child in node.children.items():
                _print(child, prefix_bin + bit, depth + 1)
        _print(self.root, '', 0)