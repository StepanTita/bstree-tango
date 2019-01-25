def set_parents(tree):
    """
    (Re)set the parent pointers in tree.

    Parent pointers can be inferred from the left and right pointers.
    This can be useful if you are building a tree manually.
    """
    if tree is None or not hasattr(tree, 'root') or tree.root is None:
        return

    tree.root.tree = tree

    def set_parent(node, parent):
        if node is None:
            return

        node.parent = parent
        set_parent(node.left, node)
        set_parent(node.right, node)

    set_parent(tree.root, None)
