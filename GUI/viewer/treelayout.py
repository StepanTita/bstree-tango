#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#---------------SYS----------------
import sys
sys.path.insert(0, '../tree/')
sys.path.insert(1, '../util/')
#--------------\SYS----------------

"""
This module defines some (binary) tree layout algorithms.
"""


class SimpleBinaryTreeLayout():

    """
    Simple top to bottom binary tree layout halfing the space between siblings
    at every level.

    Args:
        width (int): The width of the viewport in px, default 800.
        height (int): The height of the viewport in px, default 600.
        margin (int): The margin in px, default 20. The center of the nodes are
            placed on the border so it should be greater than the node radius.
    """

    def __init__(self,
                 width=1200,
                 height=720,
                 margin=20):
        self.width = width
        self.height = height
        self.margin = margin

        # node_radius seems to act like a additional margin so we don't need
        # it. It is here because it may be necessary in future if we want to
        # take the additional informations next to a node into account.
        self.node_radius = 0
    #end_init

    def layout(self, tree):
        """
        Layout a binary tree, i.e. calculate the position of each node in
        the viewport where the origin is in the top left.

        Args:
            tree (BinaryTree): the tree to layout.

        Returns:
            dict: node -> (x, y) tuple of double - the coordinates of the
                  center of the node.
        """
        pos = {}
        margin = self.margin + self.node_radius

        if tree.root:
            width = self.width - 2 * margin
            height = self.height - 2 * margin

            # the root is displayed at the top center
            y_0 = margin + height
            x_0 = margin + width/2
            pos[tree.root] = (x_0, y_0)

            # vertical spacing
            tree_depth = tree.height()
            dy = height / tree_depth if tree_depth != 0 else 0

            # horizontal spacing
            def dx(depth):
                """Returns horizontal spacing for given level:"""
                return (width / 2) / (2 ** depth)

            def pos_from_parent(node, depth, parent_pos):
                """Recursive helper to calculate position based on parent and
                depth."""
                if node:
                    y = y_0 - depth * dy

                    if node == node.parent.left:
                        x = parent_pos[0] - dx(depth)
                    else:
                        x = parent_pos[0] + dx(depth)

                    pos[node] = (x, y)

                    pos_from_parent(node.left, depth+1, (x, y))
                    pos_from_parent(node.right, depth+1, (x, y))
            #end_pos_from_parent
            pos_from_parent(tree.root.left, 1, (x_0, y_0))
            pos_from_parent(tree.root.right, 1, (x_0, y_0))
        #endif

        return pos
    #end_layout

#end_SimpleBinaryTreeLayout

class SpaceEfficientBinaryTreeLayout():

    """
    This layout is more space efficient than the SimpleBinaryTreeLayout.

    Args:
        width (int): The width of the viewport in px, default 800.
        height (int): The height of the viewport in px, default 600.
        margin (int): The margin in px, default 20. The center of the nodes are
            placed on the border so it should be greater than the node radius.
    """


    def __init__(self,
                 width=1200,
                 height=720,
                 margin=20):
        self.width = width
        self.height = height
        self.margin = margin
    #end_init


    def layout(self, tree):
        """
        Layout a binary tree, i.e. calculate the position of each node in
        the viewport where the origin is in the top left.

        Args:
            tree (BinaryTree): the tree to layout.

        Returns:
            dict: node -> (x, y) tuple of double - the coordinates of the
                  center of the node.
        """
        pos = {}

        if tree.root is None:
            return pos

        # We use virtual coordinates and dimensions since we do not know in
        # advance how big the tree is. After the layout process we
        # transform these coordinates to match the viewport. To do that we
        # keep track of the minimal and maximal used coordinates.

        # Pass 1: Layouting using virtual coordinates.
        x_0, y_0 = 0, 0
        d = 1

        def _layout_subtree(p, x_0, y_0):
            """
            Sets the virtual position off all nodes in the subtree rooted
            at p where (x_0, y_0) are the coordinates of the
            top-left corner of the region allocated for this subtree.

            Returns the required width and height of this region.
            """

            # Case 1: Empty.
            if p is None:
                # No space required.
                return 0, 0

            # Case 2: Leaf.
            elif p.left is None and p.right is None:
                pos[p] = x_0, y_0
                # Spacing is managed by parents.
                return 0, 0
            #endif

            # Case 3: Has child(ren).
            left_width, left_height = _layout_subtree(
                p.left,
                x_0,
                y_0 + d)

            if p.left is None:
                # we do not need d/2 spacing
                x = x_0
            else:
                x = x_0 + left_width + d/2
            #endif

            pos[p] = (x, y_0)

            right_width, right_height = _layout_subtree(
                p.right,
                x + d/2,
                y_0 + d)

            # required_width = left_width + d + right_width
            required_width = left_width + right_width
            if p.left is not None:
                required_width += d/2
            if p.right is not None:
                required_width += d/2

            required_height = max(left_height, right_height) + d

            return required_width, required_height
        #end_layout_subtree

        total_width, total_height = _layout_subtree(tree.root, x_0, y_0)

        # Pass 2: scaling
        # map 0, 0 to margin, margin
        # and total_width, total_height to width - margin, height - margin
        if total_width == 0 and total_height == 0:
            # there is only the root node
            pos[tree.root] = (self.width/2, self.margin + self.height)
        else:
            viewport_width = self.width - 2 * self.margin
            viewport_height = self.height - 2 * self.margin

            scale_x = viewport_width / total_width
            scale_y = viewport_height / total_height

            for node, (x, y) in pos.items():
                x = x * scale_x + self.margin
                y = y * scale_y + self.margin
                pos[node] = (x, self.height - y)
            #endfor
        #endif

        return pos
    #end_layout
#end_SpaceEfficientBinaryTreeLayout

def show_layout(layout, keys):
    from naive import NaiveBST
    from treeview import TreeView

    t = NaiveBST()
    tv = TreeView(t, layout_algorithm=layout)

    for key in keys:
        t.insert(key)
        tv.view()


def main():
    from random import shuffle

    keys = list(range(32))
    shuffle(keys)

    show_layout(SimpleBinaryTreeLayout, keys)
    show_layout(SpaceEfficientBinaryTreeLayout, keys)


if __name__ == '__main__':
    main()
