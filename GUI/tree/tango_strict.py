#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is a implementation of Tango Trees as described in
"Dynamic Optimality - Almost" by ERIK D. DEMAINE, DION HARMON,
JOHN IACONO, AND MIHAI PATRASCU.


It tries to use the proposed strict model, i.e. using only one pointer p at
all times and allowing only the following unit-cost operations
 - go left  (p = p.left)
 - go right (p = p.right)
 - go up    (p = p.parent)
 - rotate with parent (p.rotate())
on it.

Furthermore the access algorithm is not allowed to save extra data.

The choice of the next operation is a function only of the data of the node
currently pointed to.
You can write data after each operation on the node pointed by p.
The data should have constant size so it can be read and written in constant
time (in the RAM model).

The access algorithm's goal is to set p to the node with the desired key.

In general it has the following structure:

    def search(key):
        p = root
        p.search_key = key

        while True:
            data = p.getData()  # returning p and all fields of p
            operation, data = access_algorithm(data)
            if operation == RIGHT:
                p = p.right
            elif operation == LEFT:
                p = p.left
            elif operation == UP:
                p = p.parent
            elif operation == ROTATE:
                p.rotate()
            else:
                break
            p.setData(data)

        return p.data

where access_algorithm is a function mapping a node's data to an operation and
the data to write after the operation.


Implementation note
-------------------
A (sane) programm can (?) be transformed to a function of the required form by
saving the state of the programm in the node. This includes the line you are at
and all local variables.

So you are model-conform if you use only constant space and no additional
pointers.

TODO Proof this :)


Implementation note
-------------------
You can still use statements like

    if p.parent.right.color == RED:
        ..

because they can be rewritten as:

    # go to node
    key = self.key
    p = p.parent

    p = p.right

    # retrieve the value
    val = p.color

    # go back
    p = p.parent

    p = p.left
    if p.key != key:
        # we should have chosen the right child
        p = p.parent
        p = p.right

    if val == RED:
        ..

This uses only extra space proportional to the length of the code which
is constant.

Implementation note
-------------------
You can even use aliases if you do not modify p before using the alias.

    pp = p.parent
    pp.color = BLACK    // OK - you could substitute pp with p.parent
    p = p.right
    // pp.color = RED   // ERROR - pp is now p.parent.parent
"""

#--------------------AUX TREES-----------------------
from tree.bintree import BinaryTree
from tree.rb import RBNode, RED, BLACK
from tree.naive import perfect_inserter
#-------------------\AUX TREES-----------------------

import time
import datetime as dt

#----------------------CONST-------------------------
SEARCH_START = 10
SEARCH_END = 20
SEARCH_SUCCESS = 30
CUT = 40
JOIN = 50
#---------------------\CONST-------------------------

def is_root_or_None(node):
    """
    Returns True if node is None or the root of a new auxiliary tree,
    otherwise False.
    """
    return node is None or node.is_root
#end_is_root_or_None

class TangoNode(RBNode):

    """
    Attributes:
        key
        data
        parent
        left
        right
        tree
        color: inherited from RBTree (to balance auxiliary tree).
        bh: Black-Height from RBTree (concatenate).
        depth (int): depth of node in the perfect BST P (constant over time).
        min_depth (int): The minimum depth of all nodes in auxiliary tree.
        max_depth (int): The maximum depth of all nodes in auxiliary tree.
        is_root (bool): True if this node is the root of an auxiliary tree.
    """

    def __init__(self, key,
                 data=None, parent=None, left=None, right=None, tree=None,
                 color=BLACK, bh=1,
                 depth=0, is_root=True):

        super().__init__(key, data, parent, left, right, tree, color, bh)

        self.depth = depth
        # Infer min_depth and max depth from left and right children
        # and own depth.
        self._update_depths()

        self.is_root = is_root

    #end__init__

    def _update_depths(self):
        """
        Infer (recursivly defined) min_depth and max_depth from children.

        *_depth = *(self.depth, self.left.*_depth, self.right.*_depth)
        where * = min or max
        """

        self.min_depth = self.depth
        self.max_depth = self.depth

        if not is_root_or_None(self.left):
            self.min_depth = min(self.min_depth, self.left.min_depth)
            self.max_depth = max(self.max_depth, self.left.max_depth)

        if not is_root_or_None(self.right):
            self.min_depth = min(self.min_depth, self.right.min_depth)
            self.max_depth = max(self.max_depth, self.right.max_depth)
    #end_update_depths


    # The following methods are only used as node_attributes for TreeView.
    @property
    def ir(self):   # is_root
        return self.is_root

    @property
    def d(self):
        return self.depth

    @property
    def min_d(self):
        return self.min_depth

    @property
    def max_d(self):
        return self.max_depth
#end_TangoNode

class TangoTree(BinaryTree):

    """
    Tango Trees are a class of O(log log n)-competetive binary search trees.
    They only support searches.

    Args:
        keys (list): The static universe of keys.
    """

    def __init__(self, keys):
        super().__init__()

        if not keys:
            raise AttributeError("No keys given")

        # We want to use insert() to construct the initial tree.
        # After that we disable insert() by setting constructed to True.
        self.constructed = False

        # Create perfect tree P (using insert()).
        # TODO This is only a O(n log n) solution.
        perfect_inserter(self, sorted(keys))
        self.constructed = True

        # Set min_depth and max_depth of each node.
        def fix_depth(node, depth=0):
            # d = min_d = max_d because each node forms its own auxiliary tree
            # You could also invoke _update_depths() on each node.
            if node:
                fix_depth(node.left, depth + 1)
                fix_depth(node.right, depth + 1)
                node.depth = node.min_depth = node.max_depth = depth
            #endif
        #end_fix_depth

        self.search_log = [] # a list with a log of operations
        self.parody = ParodyTree()

        self.parody.create_parody(self.root)
        self.step = True

        fix_depth(self.root)
    #end__init__

    def insert(self, key, data=None):
        """A naive insert function only used to construct the tree."""
        if self.constructed:
            raise NotImplementedError(
                "Original Tango Trees do not support insert")

        if self.root is None:
            self.root = TangoNode(key, tree=self)
            return

        p = self.root
        parent = None
        is_left_child = False

        while p is not None:
            if key < p.key:
                parent = p
                p = p.left
                is_left_child = True
            elif key > p.key:
                parent = p
                p = p.right
                is_left_child = False
            #endif
        #endwhile

        p = TangoNode(key, parent=parent)
        if is_left_child:
            parent.left = p
        else:
            parent.right = p
    #end_insert

    def search(self, key):
        start = time.time()
        """
        Search for key in the tree.

        The search is only defined for accesses, i.e. keys that are actually
        in the tree.

        Returns:
            The reference p of a node with p.key == key.
        """
        self.search_log.append({'text' : "Start search for {}".format(key), 
            'act' : SEARCH_START, 'time' : 0, 'highlight' : True})

        # Start at the root.
        p = self.root

        # We do a normal BST walk.
        while p is not None:
            if p.key < key:
                p = p.right
            elif p.key > key:
                p = p.left
            else:
                break #<------------------------------------------------------------------------------------------------------------
            #endif

            # If we visit a marked node we have to modifiy the preferred paths
            # 1 Cut auxiliary tree containing the parent of p at p.min_depth-1.
            #       into a top and a bottom path.
            # 2 Join the top path with auxiliary tree rooted at p.
            if p is not None and p.is_root:
                depth = p.min_depth - 1
                n = p
                p = p.parent
                p = self._new_cut(p, depth)
                p = self._new_join(p, n, depth)
            #endif
        #endwhile

        # The while loop has terminated so p.key == key.
        # If the searched node was a root we are now at the root again
        # so we make sure that p.key = key again
        # TODO Test if this breaks something again.
        # if p.key != key:
        #     p = self._aux_search(key, p)

        # Finally set the preferred child of the access p to left.
        # 1 cut its auxiliary tree at depth p.depth
        # 2 join with preceding marked node
        #print("final cut&join")----------------------------------------------------------------------
        r = None
        if p is not None:
            r = self._cut_at(p)

        marked_p = None
        if not r is None:
            marked_p = self.find_marked_predeccessor(r, p.key)

        if marked_p is not None:
            self._new_join(r, marked_p, p.depth)

        #print("Search: Found", p.key)----------------------------------------------------------------
        end = time.time()
        if p is not None:
            self.search_log.append({'text' : "Search: Found {}".format(p.key), 
                'act' : SEARCH_SUCCESS, 'time' : end - start, 'highlight' : False})
        else:
            self.search_log.append({'text' : "Search: key not found", 
                'act' : SEARCH_END, 'time' :  end - start, 'highlight' : False})

        self.parody.find(self.parody.root, key)
        if p is not None:
            return p.key
        else:
            return None
    #end_search

    def _aux_search(self, key, root):
        """
        Search key in the auxiliary tree with the given root.

        Returns:
            Either the node with the given key or
            the leaf where the search ends.
        """
        # Do an ordinary search until the next node would be a root or None.
        p = root
        while p.key != key:
            if p.key < key:
                if not is_root_or_None(p.right):
                    p = p.right
                else:
                    # print("\taux_search of {} in {} ended in leaf {}".format(
                    #     key, root.key, p.key))
                    # self.view(highlight_nodes=[p])
                    return p
                #endif
            elif p.key > key:
                if not is_root_or_None(p.left):
                    p = p.left
                else:
                    # print("\taux_search of {} in {} ended in leaf {}".format(
                    #     key, root.key, p.key))
                    # self.view(highlight_nodes=[p])
                    return p
                #endif
            #endif
        #endwhile
        #print("\taux_search of {} in {} successful".format(
        #    key, root.key))----------------------------------------------------------------------------------------------------------
        # self.view(highlight_nodes=[p])
        return p
    #end_aux_search

    def _aux_go_to_root(self, p):
        """
        Returns the root of the auxiliary tree containing p.
        """
        if p is None:
            return None

        while not p.is_root:
            p = p.parent
        #print("\tgoing up to", p.key)------------------------------------------------------------------------------------------------
        # self.view(highlight_nodes=[p])
        return p
    #end_aux_go_to_root

    
    def update_black_height(self, p):

        if p is None:
            return
        lh = 0
        rh = 0

        if self.has_left(p):
            lh = p.left.bh

        if self.has_right(p):
            rh = p.right.bh

        p.bh = lh

        if p.color == BLACK:
            p.bh += 1
    #end_update_black_height

    def _aux_update_bh(self, n):

        self.update_black_height(n)

        while not self.is_root(n):
            n = n.parent
            self.update_black_height(n)


    def _new_cut(self, p, cut_depth):
        """
        Cut the auxiliary tree containing p into two auxiliary trees, one
        containing all nodes with depth <= d and one with depths > d.

        Returns:
            The root of the top path.
        """
        # TODO explain cutting
        #print("Cut at", p.key, "depth", cut_depth)------------------------------------------------------------------
        t_key = p.key
        start = time.time()

        new_root = None
        p = self._aux_go_to_root(p)

        l = self.min_with_depth(p, cut_depth)
        r = self.max_with_depth(p, cut_depth)

        lp = None
        if l is not None:
            lp = self._get_predecessor(l)
        rp = None
        if r is not None:
            rp = self._get_successor(r)

        if lp is None and rp is None:
            new_root = p
        elif rp is None:

            self._split(lp, p)

            if lp.right is not None:
                self.mark_node(lp.right)
            self._aux_update_depths(lp)

            new_root = self._aux_merge(lp)

        elif lp is None:

            self._split(rp, p)

            if rp.left is not None:
                self.mark_node(rp.left)
            self._aux_update_depths(rp)

            new_root = self._aux_merge(rp)

        else:

            self._split(lp, p)
            self._split(rp, lp.right)

            if rp.left is not None:
                self.mark_node(rp.left)
            self._aux_update_depths(rp)

            self._aux_merge(rp)
            new_root = self._aux_merge(lp)
        #endif
        #print(self._viewer)
        if self.step:
            self.view(highlight_nodes=[new_root])

        #self.parody.update_roots(self.parody.root)

        #self.parody.view()
        end = time.time()
        self.search_log.append({'text' : "Cut at {}".format(t_key), 
            'act' : CUT, 'time' : end - start, 'highlight' : False})

        return new_root

    def _new_join(self, top_path, n, cut_depth):

        start = time.time()
        new_root = None

        lp = None
        rp = None

        p = top_path

        while p is not None and p != n:
            if p.key > n.key:
                rp = p
                p = p.left
            else:
                lp = p
                p = p.right
        #endif

        if lp is None and rp is None:
            raise Exception("SHOULDN`T HAPPEN")
        elif rp is None:

            self._split(lp, top_path)

            if lp.right is not None:
                self.unmark_node(lp.right)
                self._aux_update_depths(lp.right)
            else:
                self._aux_update_depths(lp)

            new_root = self._aux_merge(lp)
        elif lp is None:

            self._split(rp, top_path)

            if rp.left is not None:
                self.unmark_node(rp.left)
                self._aux_update_depths(rp.left)
            else:
                self._aux_update_depths(rp)

            new_root = self._aux_merge(rp)

        else:

            self._split(lp, top_path)
            self._split(rp, lp.right)

            if rp.left is not None:
                self.unmark_node(rp.left)
                self._aux_update_depths(rp.left)
            else:
                self._aux_update_depths(rp)

            self._aux_merge(rp)

            new_root = self._aux_merge(lp)
        #endif

        if self.step:
            self.view()

        #self.parody.update_roots(self.parody.root)
        #self.parody.view()
        end = time.time()
        self.search_log.append({'text' : "Join at {}".format(top_path.key), 
            'act' : JOIN, 'time' : end - start, 'highlight' : False})

        return new_root


    def _aux_update_depths(self, p):
        """
        Update the min_depth and max_depth of p and its ancestors in auxiliary
        tree.

        This is be needed if you mark or unmark a node thus changing an
        auxiliary tree.

        Returns:
            The argument p.
        """
        p._update_depths()
        p_key = p.key

        while not self.is_root(p):
            p = p.parent
            p._update_depths()

        # go down to the saved key again
        p = self._aux_search(p_key, p)

        return p

    # The methods _find_predecessor(self, p) and _find_successor(self, p)
    # do not return p.
    def _find_predecessor(self, p):
        """
        Returns the predecessor of a node in an auxiliary tree if it exists,
        otherwise p itself.

        Returns:
            (pred, True) if pred is the predecessor of p, otherwise
            (p, False) if there is no predecessor.
        """
        # Case 1: left subtree is not empty
        #   the maximum node of the left subtree is the predecessor
        if not is_root_or_None(p.left):
            # if left child exists go left and then all the way right
            p = p.left
            while not is_root_or_None(p.right):
                p = p.right
            return p, True

        # Case 2: left subtree is empty
        #   go up until we come from a right child
        #   this parent is the predecessor
        # Case 3: no parent (and left subtree) exists
        #   there is no predecessor
        p_key = p.key
        while True:
            if self.is_root(p):
                # Case 3: no predecessor
                # We have to go back to p
                p = self._aux_search(p_key, p)
                return p, False
            if p == p.parent.right:
                return p.parent, True
            else:
                p = p.parent    # go up

    def _find_successor(self, p):
        """
        Returns the successor of a node in an auxiliary tree if it exists,
        otherwise p itself.

        Returns:
            (succ, True) if succ is the successor of p, otherwise
            (p, False) if there is no successor.
        """
        # This is symmetric with _find_predecessor swapping left and right.

        # Case 1: right subtree is not empty
        #   the maximum node of the right subtree is the successor
        if not is_root_or_None(p.right):
            # if right child exists go right and then all the way left
            p = p.right
            while not is_root_or_None(p.left):
                p = p.left
            return p, True

        # Case 2: right subtree is empty
        #   go up until we come from a left child
        #   this parent is the successor
        # Case 3: no parent (and right subtree) exists
        #   there is no successor
        p_key = p.key
        while True:
            if self.is_root(p):
                # Case 3: no successor
                # We have to go back to p
                p = self._aux_search(p_key, p)
                return p, False
            if p == p.parent.left:
                return p.parent, True
            else:
                p = p.parent    # go up

#------------------------------------------------TEST----------------------------------------------------

    def is_root(self, p):
        return p.is_root or p.parent is None

    def has_left(self, p):
        return p.left is not None and not p.left.is_root

    def has_right(self, p):
        return p.right is not None and not p.right.is_root

    def is_left_child(self, p):
        return p == p.parent.left

    def is_right_child(self, p):
        return p == p.parent.right

    def is_black(self, p):
        return p.color == BLACK

    def is_red(self, p):
        return p.color == RED

    def get_sibling(self, n):

        if self.is_root(n):
            return None
        else:
            if self.is_left_child(n) and self.has_right(n.parent):
                return n.parent.right
            elif self.is_right_child(n) and self.has_left(n.parent):
                return n.parent.left
            else:
                return None

    def clear_parent_reference(self, n):
        if n == n.parent.left:
            n.parent.left = None
        elif n == n.parent.right:
            n.parent.right = None

    def set_parent_reference(self, p, n):
        if p == p.parent.left:
            p.parent.left = n
        elif p == p.parent.right:
            p.parent.right = n


    def detach(self, child, parent):
        if child is None:
            return
        self.clear_parent_reference(child)
        child.parent = None

    def attach_up(self, child, parent):
        if child is None:
            return
        if child.key < parent.key:
            parent.left = child
        else:
            parent.right = child
        child.parent = parent

    def attach_left(self, child, parent):
        if child is None:
            return
        parent.left = child
        child.parent = parent

    def attach_right(self, child, parent):
        if child is None:
            return
        parent.right = child
        child.parent = parent

    def mark_node(self, node):
        node.is_root = True

    def unmark_node(self, node):
        node.is_root = False

    def get_max_child(self, p):
        prev = p
        while self.has_right(p):
            prev = p
            p = p.right
        if prev.right is not None and not prev.right.is_root:
            return prev.right
        return prev
    #end_get_max_child

    def get_min_child(self, p):
        prev = p
        while self.has_left(p):
            prev = p
            p = p.left
        if prev.left is not None and not prev.left.is_root:
            return prev.left
        return prev
    #end_get_min_child

    def find_min_with_bh(self, p, bh):
        while not is_root_or_None(p):

            if p.color == BLACK and p.bh == bh:
                break
            p = p.left
        return p

    def find_max_with_bh(self, p, bh):
        while not is_root_or_None(p):

            if p.color == BLACK and p.bh == bh:
                break;
            p = p.right
        return p

    def min_with_depth(self, p, cut_depth):

        while p is not None:
            pl = p.left
            pr = p.right

            if not is_root_or_None(pl) and pl.max_depth > cut_depth:
                p = pl
            elif p.depth > cut_depth:
                break
            elif not is_root_or_None(pr):
                p = pr
            else:
                return None
        return p

    def max_with_depth(self, p, cut_depth):

        while p is not None:
            pl = p.left
            pr = p.right

            if not is_root_or_None(pr) and pr.max_depth > cut_depth:
                p = pr
            elif p.depth > cut_depth:
                break
            elif not is_root_or_None(pl):
                p = pl
            else:
                return None
        return p


    def attach_as_max(self, n, t):

        if t is None or n is None:
            return 
        a = self.get_max_child(t)
        ar = a.right

        self.detach(ar, a)
        self.attach_left(ar, n)

        self.attach_right(n, a)

        self._aux_update_depths(n)

    def attach_as_min(self, n, t):

        if t is None or n is None:
            return
        a = self.get_min_child(t)
        al = a.left

        self.detach(al, a)
        self.attach_right(al, n)

        self.attach_left(n, a)

        self._aux_update_depths(n)

    def _split(self, tango_node, v_root):

        node = tango_node

        v_parent = v_root.parent

        if v_parent is not None:
            self.detach(v_root, v_parent)

        v_mark = v_root.is_root

        if v_mark:
            self.unmark_node(v_root)

        k = v_root
        tl = None
        vl = None
        tr = None
        vr = None

        while not is_root_or_None(k):

            kl = k.left
            kr = k.right

            self.detach(kl, k)
            self.detach(kr, k)

            if kl is not None:
                kl.color = BLACK
                self.update_black_height(kl)

            if kr is not None:
                kr.color = BLACK
                self.update_black_height(kr)

            if node.key < k.key:
                tr = self._merge(kr, vr, tr)

                vr = k
                k = kl
            elif node.key > k.key:
                tl = self._merge(tl, vl, kl)

                vl = k
                k = kr
            else:
                tl = self._merge(tl, vl, kl)
                vl = None

                tr = self._merge(kr, vr, tr)
                vr = None

                self.attach_left(tl, k)
                self.attach_right(tr, k)

                break
            #endif
        #endwhile

        if v_parent is None:
            self.root = node
        else:
            self.attach_up(node, v_parent)

        if v_mark:
            self.mark_node(node)

        #self.view()
        return node

    def _aux_merge(self, n):

        np = n.parent
        nl = n.left
        nr = n.right
        root_mark = False

        if n.is_root:
            root_mark = True
            self.unmark_node(n)

        if np is not None:
            self.detach(n, np)

        self.detach(nl, n)
        self.detach(nr, n)

        n.color = BLACK
        self.update_black_height(n)

        if nl is not None:
            nl.color = BLACK
            self.update_black_height(nl)

        if nr is not None:
            nr.color = BLACK
            self.update_black_height(nr)

        new_root = self._merge(nl, n, nr)

        if np is None:
            self.root = new_root
        else:
            self.attach_up(new_root, np)

        if root_mark:
            self.mark_node(new_root)

        return new_root

    def _merge(self, nl, n, nr):

        if n is None:

            if nr is not None:
                n = nr
            elif nl is not None:
                n = nl
            else:
                return
                raise Exception("SHOULDN`T HAPPEN")

        elif is_root_or_None(nl) and is_root_or_None(nr):

            self.attach_left(nl, n)

            self.attach_right(nr, n)

            n.color = RED
            self.update_black_height(n)

        elif is_root_or_None(nl):

            self.attach_as_min(n, nr)

            self.attach_left(nl, n)

            n.color = RED
            self.update_black_height(n)
        elif is_root_or_None(nr):

            self.attach_as_max(n, nl)

            self.attach_right(nr, n)

            n.color = RED
            self.update_black_height(n)
        else:

            lh = nl.bh
            rh = nr.bh

            if lh == rh:

                self.attach_left(nl, n)
                self.attach_right(nr, n)

                n.color = RED
            elif lh < rh:

                p = self.find_min_with_bh(nr, nl.bh)
                pp = p.parent

                self.attach_left(nl, n)

                self.detach(p, pp)

                self.attach_right(p, n)

                self.attach_left(n, pp)

                self._aux_update_depths(n)

                n.color = RED
            else:

                p = self.find_max_with_bh(nl, nr.bh)

                pp = p.parent

                self.attach_right(nr, n)

                self.detach(p, pp)
                self.attach_left(p, n)

                self.attach_right(n, pp)
                self._aux_update_depths(n)

                n.color = RED
            #endif
        #endif

        self._aux_update_depths(n)

        self.insert_fixup_case1(n)

        self._aux_update_bh(n)

        new_root = n
        while new_root.parent is not None:
            new_root = new_root.parent

        #self.view()

        return new_root

    def _cut_at(self, p):
        top_path = p

        while not top_path.is_root:
            top_path = top_path.parent
        cut_depth = p.depth
        top_path = self._new_cut(top_path, cut_depth)

        return top_path

    def find_marked_predeccessor(self, root, key):
        key -= 1
        n = root

        while n is not None:

            if key < n.key:
                n = n.left
            elif key > n.key:
                n = n.right
            else:
                return None

            if n is not None and n.is_root:
                return n
        return None

    #---------------INSERT FIXUP-----------------
    def insert_fixup_case1(self, n):
        if self.is_root(n):
            n.color = BLACK
            self.update_black_height(n)
        else:
            self.update_black_height(n)
            self.insert_fixup_case2(n)


    def insert_fixup_case2(self, n):

        p = n.parent
        if self.is_black(p):
            self.update_black_height(p)
            return
        else:
            self.insert_fixup_case3(n)


    def insert_fixup_case3(self, n):

        p = n.parent
        g = p.parent
        u = self.get_sibling(p)

        if u is not None and self.is_red(u):
            p.color = BLACK
            self.update_black_height(p)
            u.color = BLACK
            self.update_black_height(u)

            g.color = RED
            self.update_black_height(g)

            self.insert_fixup_case1(g)
        else:
            self.insert_fixup_case4(n)


    def insert_fixup_case4(self, n):

        p = n.parent

        if self.is_left_child(p):
            if self.is_right_child(n):
                self.rotate_left(p)

                self.update_black_height(p)
                self.update_black_height(n)

                n = p
        else:

            if self.is_left_child(n):
                self.rotate_right(p)

                self.update_black_height(p)
                self.update_black_height(n)

                n = p

        self.insert_fixup_case5(n)


    def insert_fixup_case5(self, n):

        p = n.parent
        g = p.parent

        p.color = BLACK
        g.color = RED

        if self.is_left_child(p):
            self.rotate_right(g)
        else:
            self.rotate_left(g)

        self.update_black_height(g)
        self.update_black_height(p)


    #-----------------------ROTATIONS-----------------

    def rotate_left(self, n):

        pv = n.right
        pv.parent = n.parent

        if n.parent is None:
            if n == self.root:
                root = pv
            else:
                pass
        else:
            if n is not None:
                self.set_parent_reference(n, pv)

        n.right = pv.left

        if n.right is not None:
            n.right.parent = n

        pv.left = n
        n.parent = pv

        if n.is_root:
            self.mark_node(n.parent)
            self.unmark_node(n)

        self._aux_update_depths(n)
        self._aux_update_depths(n.parent)

    def rotate_right(self, n):

        pv = n.left
        pv.parent = n.parent

        if n.parent is None:
            if n == self.root:
                root = pv
            else:
                pass
        else:
            if n is not None:
                self.set_parent_reference(n, pv)

        n.left = pv.right

        if n.left is not None:
            n.left.parent = n

        pv.right = n
        n.parent = pv

        if n.is_root:
            self.mark_node(n.parent)
            self.unmark_node(n)

        self._aux_update_depths(n)
        self._aux_update_depths(n.parent)

    def _get_predecessor(self, p):
        if not is_root_or_None(p.left):
            # if left child exists go left and then all the way right
            p = p.left
            while not is_root_or_None(p.right):
                p = p.right
            return p

        p_key = p.key
        while True:
            if self.is_root(p):
                # Case 3: no predecessor
                # We have to go back to p
                p = self._aux_search(p_key, p)
                return None
            if p == p.parent.right:
                return p.parent
            else:
                p = p.parent    # go up

    def _get_successor(self, p):

        if not is_root_or_None(p.right):
            # if right child exists go right and then all the way left
            p = p.right
            while not is_root_or_None(p.left):
                p = p.left
            return p

        p_key = p.key
        while True:
            if self.is_root(p):
                # Case 3: no successor
                # We have to go back to p
                p = self._aux_search(p_key, p)
                return None
            if p == p.parent.left:
                return p.parent
            else:
                p = p.parent    # go up
#end_TangoTree

import sys
sys.path.insert(2, '../viewer/')
from viewer.treeview import NodeShape


def node_shape(node):
    if node.is_root:
        return NodeShape.square
    else:
        return NodeShape.circle


class ParodyNode(TangoNode):

    def __init__(self, original):

        super().__init__(key=original.key, data=original.data, is_root=original.is_root)
        self.original = original
    #end__init__

class ParodyTree(BinaryTree):

    def __init__(self, root=None):
        super().__init__()
    #end__init__


    def create_parody(self, v):
        if v is None:
            return v
        if self.root is None:
            self.root = ParodyNode(v)
            self.root.left = self.create_parody(v.left)
            self.root.right = self.create_parody(v.right)

            if self.root.left is not None:
                self.root.left.parent = self.root
            if self.root.right is not None:
                self.root.right.parent = self.root
            v.parody = self.root
            return self.root
        else:
            u = ParodyNode(v)
            u.left = self.create_parody(v.left)
            u.right = self.create_parody(v.right)

            if u.left is not None:
                u.left.parent = u
            if u.right is not None:
                u.right.parent = u
            v.parody = u
            return u

    def find(self, node, key):
        if node is None:
            return
        node.is_root = False
        if node.key > key:
            if node.right is not None:
                node.right.is_root = True
            self.find(node.left, key)
        elif node.key < key:
            if node.left is not None:
                node.left.is_root = True
            self.find(node.right, key)
        else:
            return


def main():
    t = TangoTree(range(1, 16))

    t.search(13)
    t.search(2)
    t.search(9)
    t.search(7)
    t.search(6)
    t.search(4)
    t.search(7)
    t.search(9)
    t.search(12)
    t.search(14)
    t.search(15)
    t.search(11)
    t.search(1)
    t.search(2)
    #t.search(11)
    #tv.view()


def sample_tree():
    # manually setup a sample tree
    universe = range(1, 16)
    t = TangoTree(universe)
    nodes = dict()

    #                  key, data, pare, left,    right,     tree, color, bh,d, ir
    nodes[1] = TangoNode(1, None, None, None,     None,     None, BLACK, 1, 3, True)

    nodes[7] = TangoNode(7, None, None, None,     None,     None, BLACK, 1, 3, True)

    nodes[5] = TangoNode(5, None, None, None,     None,     None, RED,   0, 3, False)
    nodes[6] = TangoNode(6, None, None, nodes[5], nodes[7], None, BLACK, 1, 2, True)

    nodes[9] = TangoNode(9, None, None, None,     None,     None, BLACK, 1, 3, True)

    nodes[10] = TangoNode(10, None, None, nodes[9], None,   None, RED,   0, 2, False)
    nodes[11] = TangoNode(11, None, None, nodes[10], None,  None, BLACK, 1, 3, True)

    nodes[13] = TangoNode(13, None, None, None,   None,     None, BLACK, 1, 3, True)

    nodes[12] = TangoNode(12, None, None, nodes[11], nodes[13], None, RED, 0, 1, False)
    nodes[15] = TangoNode(15, None, None, None,   None,     None, RED,   0, 3, False)
    nodes[14] = TangoNode(14, None, None, nodes[12], nodes[15], None, BLACK, 1, 2, True)

    nodes[3] = TangoNode(3, None, None, None,     None,     None, RED,   0, 3, False)
    nodes[2] = TangoNode(2, None, None, nodes[1], nodes[3], None, BLACK, 1, 2, False)
    nodes[8] = TangoNode(8, None, None, nodes[6], nodes[14], None, BLACK, 1, 0, False)
    nodes[4] = TangoNode(4, None, None, nodes[2], nodes[8], None, BLACK, 2, 1, True)

    t.root = nodes[4]

    from copy.util import set_parents
    set_parents(t)

    from copy.viewer import TreeView
    print(tv)
    tv = TreeView(t,
                  node_attributes=['d', 'min_d', 'max_d'], width=800,
                  node_shape=node_shape)
    #tv.view()
    #t.search(9)
    #tv.view()
    return tv

if __name__ == '__main__':
    #sample_tree()
    main()
