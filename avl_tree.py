# avl_tree.py

class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def __init__(self):
        self.root = None

    def _height(self, node):
        if not node:
            return 0
        return node.height

    def _balance(self, node):
        if not node:
            return 0
        return self._height(node.left) - self._height(node.right)

    def _update_height(self, node):
        if not node:
            return
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    def _rotate_right(self, y):
        x = y.left
        T2 = x.right

        x.right = y
        y.left = T2

        self._update_height(y)
        self._update_height(x)

        return x

    def _rotate_left(self, x):
        y = x.right
        T2 = y.left

        y.left = x
        x.right = T2

        self._update_height(x)
        self._update_height(y)

        return y

    def insert(self, key, value):
        self.root = self._insert(self.root, key, value)

    def _insert(self, root, key, value):
        if not root:
            return Node(key, value)

        if key < root.key:
            root.left = self._insert(root.left, key, value)
        elif key > root.key:
            root.right = self._insert(root.right, key, value)
        else:
            # Key already exists, update the value
            root.value = value
            return root

        self._update_height(root)

        balance = self._balance(root)

        # Left Heavy
        if balance > 1:
            if key < root.left.key:
                return self._rotate_right(root)
            else:
                root.left = self._rotate_left(root.left)
                return self._rotate_right(root)

        # Right Heavy
        if balance < -1:
            if key > root.right.key:
                return self._rotate_left(root)
            else:
                root.right = self._rotate_right(root.right)
                return self._rotate_left(root)

        return root
