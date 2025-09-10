"""
Módulo BTreeIndex para snapshots de configuración.
"""

class BTreeNode:
    def __init__(self, order):
        self.order = order
        self.keys = []
        self.values = []
        self.children = []
        self.leaf = True

class BTreeIndex:
    def __init__(self, order=4):
        self.root = BTreeNode(order)
        self.order = order
        self.height = 1
        self.splits = 0
        self.merges = 0
        self.nodes = 1

    def insert(self, key, value):
        # Inserta un par clave-valor (key: nombre/timestamp, value: archivo)
        root = self.root
        if len(root.keys) == 2 * self.order - 1:
            new_root = BTreeNode(self.order)
            new_root.children.append(self.root)
            new_root.leaf = False
            self._split_child(new_root, 0)
            self.root = new_root
            self.height += 1
            self.nodes += 1
            self.splits += 1
            self._insert_nonfull(self.root, key, value)
        else:
            self._insert_nonfull(root, key, value)

    def _insert_nonfull(self, node, key, value):
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(None)
            node.values.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i+1] = node.keys[i]
                node.values[i+1] = node.values[i]
                i -= 1
            node.keys[i+1] = key
            node.values[i+1] = value
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == 2 * self.order - 1:
                self._split_child(node, i)
                self.splits += 1
                if key > node.keys[i]:
                    i += 1
            self._insert_nonfull(node.children[i], key, value)

    def _split_child(self, parent, i):
        order = self.order
        y = parent.children[i]
        z = BTreeNode(order)
        z.leaf = y.leaf
        z.keys = y.keys[order:]
        z.values = y.values[order:]
        if not y.leaf:
            z.children = y.children[order:]
        parent.children.insert(i+1, z)
        parent.keys.insert(i, y.keys[order-1])
        parent.values.insert(i, y.values[order-1])
        y.keys = y.keys[:order-1]
        y.values = y.values[:order-1]
        if not y.leaf:
            y.children = y.children[:order]
        self.nodes += 1

    def search(self, key, node=None):
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return node.values[i]
        if node.leaf:
            return None
        return self.search(key, node.children[i])

    def inorder(self, node=None, result=None):
        if result is None:
            result = []
        if node is None:
            node = self.root
        i = 0
        for i in range(len(node.keys)):
            if not node.leaf:
                self.inorder(node.children[i], result)
            result.append((node.keys[i], node.values[i]))
        if not node.leaf:
            self.inorder(node.children[i+1], result)
        return result

    def get_stats(self):
        return {
            'order': self.order,
            'height': self.height,
            'nodes': self.nodes,
            'splits': self.splits,
            'merges': self.merges
        }