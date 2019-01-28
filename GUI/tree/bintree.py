import sys
sys.path.insert(5, '../viewer')
from viewer.treeview import Viewable


class BinaryTree(Viewable):

    """
    Base for BST implementation.

    Provides some necessary methods for plotting.
    """

    def __init__(self):
        super().__init__()
        self.root = None

    def height(self):
        """
        Determine the height of the tree.
        """
        def h(node):
            if node:
                return max(h(node.left), h(node.right)) + 1
            else:
                return -1
        return h(self.root)


class Node(object):

    """
    Representation of a node in a Binary Search Tree,
    i.e. has key, left/right child and parent
    """

    def __init__(self, key, data=None,
                 parent=None, left=None, right=None, tree=None):
        """
        root node should have tree set to adjust when rotated
        """
        self.key = key
        self.data = data
        self.parent = parent
        self.left = left
        self.right = right

        self.tree = tree

    @property
    def grand_parent(self):
        if self.parent:
            return self.parent.parent
        else:
            return None

    def rotate(self):
        """
        Rotate node with parent if present.
        """
        if self.parent is None:
            return

        parent = self.parent

        if parent.parent:
            if parent.parent.left == parent:
                parent.parent.left = self
            elif parent.parent.right == parent:
                parent.parent.right = self
        else:
            # we rotate to root -> change in tree
            self.tree = parent.tree
            self.tree.root = self
            parent.tree = None
        self.parent = parent.parent

        if parent.left == self:
            parent.left = self.right
            if self.right:
                self.right.parent = parent
            self.right = parent
        elif parent.right == self:
            parent.right = self.left
            if self.left:
                self.left.parent = parent
            self.left = parent
        parent.parent = self

    def preorder(self):
        """
        returns preorder traversal as list of keys
        """
        po = [self.key]
        if self.left:
            po.extend(self.left.preorder())
        if self.right:
            po.extend(self.right.preorder())
        return po

    def __repr__(self):
        """
            (1)
            |- (2)
            |   |- (4)
            |   |   |- (6)
            |   |   |- (7)
            |   |- (5)
            |       |- (8)
            |       |- (9)
            |- (3)
        """
        return self._repr_helper(0, ())

    def _repr_helper(self, depth, direction_sequence):
        makeFullTree = False        # render NIL childs

        prefix = "".join(direction_sequence[:-1]) + (depth > 0) * "|- "
        if self.data is None:
            self_repr = prefix + "({key})".format(key=self.key)
        else:
            self_repr = prefix + "({key}, {data})".format(
                key=self.key, data=self.data)

        if self.right:
            self_repr += "\n" + self.right._repr_helper(
                    depth + 1,
                    direction_sequence +
                        (("|\t",) if self.left or makeFullTree else ("\t",)))
        elif makeFullTree:
            self_repr += "\n" + "".join(direction_sequence) + \
                    (depth > 0) * "|- " + "NIL"
        if self.left:
            self_repr += "\n" + self.left._repr_helper(
                    depth + 1, direction_sequence + ("\t",))
        elif makeFullTree:
            self_repr += "\n" + "".join(direction_sequence) + \
                    (depth > 0) * "|- " + "NIL"

        return self_repr
