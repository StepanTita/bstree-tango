from bintree import BinaryTree, Node


class NaiveBST(BinaryTree):

    """
    An unbalanced Binary Search Tree Implementation.

    No augumented data.
    """

    def __init__(self):
        super().__init__()
        self.root = None

    def _search(self, key):
        p = self.root
        while p is not None:
            if p.key == key:
                return p.data
            elif p.key < key:
                p = p.right
            else:
                p = p.left
        raise KeyError("Key {} not found".format(key))
        return p

    def search(self, key):
        p = self._search(key)
        return p.data

    def search_functional(self, key):
        def accessAlgorithm(searchTarget):
            # the access algorithms choice for the next operation depends on
            # - the key to search (global information)
            # - the current key (local)
            # - augumenting attributes of the node
            # availible Operations
            # - move to parent/left/right
            # - rotate
            # and write augumenting information on entering (exiting?) node
            def moveLeft(p):
                return p.left

            def moveRight(p):
                return p.right

            def moveUp(p):
                return p.parent

            def rotate(p):
                p.rotate()
                return p

            def alg(p):
                # you can read p.* but not p.*.*
                # you can also write p.info etc. but p.key is fixed and
                # the pointers can only be modified with rotations
                # you must execute one of the above operations or return
                if p is None:
                    raise KeyError("Key {} not found".format(searchTarget))
                elif p.key == searchTarget:
                    return p
                elif p.key < searchTarget:
                    p = moveRight(p)
                    return alg(p)
                elif p.key > searchTarget:
                    p = moveLeft(p)
                    return alg(p)
            return alg

        alg = accessAlgorithm(key)
        p = self.root   # pointer is always initialized to root node
        p = alg(p)      # run algorithm

        return p.data

    def insert(self, key, data=None):
        """
        Insert or update data for given key.

        Returns True for insert (key is new) and
        False for update (key already present).
        """
        # TODO quick and dirty implementation
        if self.root is None:
            self.root = Node(key, data, tree=self)
            return True

        p = self.root
        parent = None
        isLeftChild = False

        while p is not None:
            if key == p.key:
                p.data = data
                return False
            elif key < p.key:
                parent = p
                p = p.left
                isLeftChild = True
            elif key > p.key:
                parent = p
                p = p.right
                isLeftChild = False

        p = Node(key, data, parent)
        if isLeftChild:
            parent.left = p
        else:
            parent.right = p
        return True

    def delete(self, key):
        pass

    def __repr__(self):
        return self.root.__repr__()

    def preorder(self):
        return self.root.preorder()


def perfect_inserter(t, keys):
    """Insert keys into tree t such that t is perfect.
    Args:
        t (BinaryTree): An empty tree.
        keys (list): A sorted list of keys.
    """
    def f(n):
        """find the point so partition n keys for a perfect tree"""
        # x = 1
        # while x <= n//2:
        #     x *= 2
        x = 1 << (n.bit_length() - 1)
        if x//2 - 1 <= (n-x):
            return x - 1
        else:
            return n - x//2

    n = len(keys)
    if n == 0:
        return
    else:
        x = f(n)
        t.insert(keys[x])
        perfect_inserter(t, keys[:x])
        perfect_inserter(t, keys[x+1:])


def usage():
    import random
    random.seed(0)  # do always the same for testing

    # tree = NaiveBST()
    # print(tree)
    # print()

    # tree.insert(2)
    # print(tree)
    # print()

    # tree.insert(1)
    # print(tree)
    # print()

    # tree.insert(3)
    # print(tree)
    # print()

    # print("Random insertions")
    # tree = NaiveBST()
    # for i in range(10):
    #   n = random.randint(1,20)
    #   print("insert", n)
    #   tree.insert(n)
    #   print(tree, end="\n\n")

    tree = NaiveBST()
    n = 16
    universe = list(range(n))
    random.shuffle(universe)
    for key in universe:
        tree.insert(key)
    # print(tree)
    # print(tree.preorder())

    node5 = tree.root.left
    node5.rotate()
    print(tree)
    # print(' '.join([str(key) for key in tree.preorder()]))

    from viewer.treeview import TreeView
    tv = TreeView(tree)
    tv.view()
    tree.root.right.rotate()
    tv.view()
    print(tree.search_functional(4))


def join():
    t = NaiveBST()

    t.insert(7)
    t.insert(4)
    t.insert(2)
    t.insert(6)
    t.insert(1)
    t.insert(3)
    t.insert(5)
    t.insert(9)
    t.insert(8)
    t.insert(10)

    from viewer.treeview import TreeView
    tv = TreeView(t)
    tv.view()

    p = t.root
    p.left.rotate()
    tv.view()
    p.left.rotate()
    tv.view()


def main():
    usage()
    # join()


if __name__ == '__main__':
    main()
