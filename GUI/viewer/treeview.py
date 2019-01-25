#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#---------------Views--------------
from treelayout import SpaceEfficientBinaryTreeLayout
#---------------\Views-------------

#-----------DASH Modules-----------
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import *
#----------\DASH Modules-----------

#----------Plotly Modules----------
import plotly.plotly as py
import plotly.graph_objs as go
#---------\Plotly Modules----------

#---------------Rest---------------
import sys
import time
import functools
import types
from enum import Enum
#--------------\Rest---------------

class NodeShape(Enum):
    circle = 1
    square = 2
#end_NodeShape


class Viewable(object):

    """
    Inherit from this to get a method to manually view the datastructure.
    """

    def __init__(self):
        super().__init__()
        self._viewer = None
    #end_init

    def view(self, *args, **kwargs):
        if self._viewer:
            #print('hi')
            self._viewer.view(*args, **kwargs)
        #end_if
    #end_view
#end_viewable

class TreeView(object):

    """Viewer for a Binary Trees.

    If your binary tree is a subclass of Viewable you can use
    self.view(**kwargs) to manually invocate a view inside the tree class.

    Note:
        A node must always represent the same key-data-pair and should not
        overwrite default __hash__ to be usable as a dictionary key.
        TODO we could add a uid to each node to identify it.

    Args:
        tree (tree.BinaryTree): A reference to the tree to be viewed.
        node_attributes (list, optional): fields of a Node as string which
            should be viewed next to the node, default [].
        # TODO view_after redesign
        view_after (list of string, optional): the name of all functions of the
            class of t that should invoke view(..) after execution,
            default [].
        width (int, optional): tk-viewport width in px, default 800.
        height (int, optional): tk-viewport height in px, default 600.
        node_radius (int, optional): radius of the nodes of the tree in px,
            default 15.
        node_shape (NodeShape, optional): a function (node) -> NodeShape
            mapping a node to it desired shape, default all circles.
        font_size (int, optional): font_size of node labels in pt, default 12.
        animation (bool, optional): animate between tree snapshots,
            default True.

    Example:
        create a binary search tree
        >>> t = RBTree()

        set up the viewer
        >>> v = TreeView(t, node_attributes=['bh'],
        # TODO view_after redesign
        ...       view_after=['insert', 'delete'])

        execute your algorithm
        >>> t.insert(4)     # invokes view(method='insert(4)')
        >>> t.insert(2)

        and view at special states
        >>> v.view(highlight_nodes=[t.root])    # highlight the root
    """

    def __init__(self, tree,
                 node_attributes=None,
                 view_after=None,
                 width=1200, height=720,
                 node_radius=20, node_shape=None,
                 font_size=12,
                 layout_algorithm=None,
                 animation=False,
                 border=10,
                 plot_bg='rgb(0, 0, 0)'
                 ):

        self.node_attribute_names = node_attributes if node_attributes else []
        self.tree = tree
        self.width = width
        self.height = height
        self.border = border
        self.node_radius = node_radius
        self.plot_bg = plot_bg


        if node_shape is not None:
            self.node_shape = node_shape
        else:
            self.node_shape = lambda n: NodeShape.circle
        #endif

        self.font = None
        self.small_font = None

        self._precalculate_attrs(font_size)

        if layout_algorithm is not None:
            self.layout_algorithm = layout_algorithm
        else:
            self.layout_algorithm = SpaceEfficientBinaryTreeLayout
        #endif

        self.animation = animation
        self.end_pause = False   # controls the display loop
        self.redraw = False      # set to True if redraw is needed

        # Each display() creates a snapshot of the tree.
        # A snapshot is a dict with the following data:
        #   - 'nodes': {node: ((x,y), node.__dict__) for all nodes}
        #   - 'root': tree.root
        #   - 'info': the kwargs passed to view(..), e.g. the current method of
        #       the alg
        # The display position of the nodes is saved for animation.
        # TODO do we need an initial snapshot?

        self.current_snapshot_index = 0
        self.figures = []
        self.snapshots = [self._create_snapshot()]
        # TODO (low priority) do incremental versions :)

        # provide self.view(**kwargs)
        #print(self.tree)
        #print(isinstance(self.tree, Viewable))
        #if isinstance(self.tree, Viewable):
        self.tree._viewer = self

        # and wrap methods to invoke view
        if view_after is not None:
            self._view_after(view_after)

    #end_init


    def continue_callback(self, event=None):
        self.end_pause = True   # exit the event loop


    def previous_callback(self, event=None):
        return self._view(self.current_snapshot_index - 1)


    def next_callback(self, event=None):
        return self._view(self.current_snapshot_index + 1)


    def close_callback(self, event=None):
        pass


    """
    Returns the new snapshot (status of the tree) after update
    """
    def _create_snapshot(self):

        snapshot = {
            'nodes': {},
            'root': self.tree.root,
            'width': self.width,        # canvas dimensions for scaling
            'height': self.height,
            'info': {}
        }

        # calculate the position in viewport
        #print(self.layout_algorithm)
        viewer_obj = self.layout_algorithm(width=self.width, height=self.height, margin=2*self.node_radius)
        pos = viewer_obj.layout(self.tree)

        for node, position in pos.items():
            # save other attributes
            snapshot['nodes'][node] = (
                position,
                node.__dict__.copy(),
                [getattr(node, name) for name in self.node_attribute_names],
                self.node_shape(node)
            )
        #endfor

        return snapshot
    #end_create_shapshot


    """
    Estimates the suitable font size and node_radius
    """
    def _precalculate_attrs(self, font_size):

        import pyautogui
        screen_width = pyautogui.size()[0]
        keys = 2 ** (self.tree.height() - 1)
        self.node_radius = screen_width // keys
        if self.node_radius < 20:
            self.node_radius = 20
        elif self.node_radius > 35:
            self.node_radius = 35
        self.font = ('Verdana', self.node_radius // 2)
        self.small_font = ('Verdana', font_size // 2)


    """
    Creates annotations list for the tree nodes
    """
    def make_annotations(self, font_size=20, font_color='rgb(250,250,250)'):

        annotations = dict() #go.Annotations()
        nodes = self.snapshots[self.current_snapshot_index]['nodes']

        for node, value in nodes.items():
            annotations[node] = go.Annotation(
                        text=node.key, # or replace labels with a different list for the text within the circle 
                        x=value[0][0], y=value[0][1],
                        xref='x1', yref='y1',
                        font=dict(color=font_color, size=font_size),
                        showarrow=False
                    )
        #endfor

        return annotations
    #end_make_annotations

    def create_layout(self):
        layout = dict(#title= 'Tree Layout Algorithm',  
                    showlegend=False,
                    xaxis={
                        'showline' : False, # hide axis line, grid, ticklabels and  title
                        'zeroline' : False,
                        'showgrid' : False,
                        'showticklabels' : False,
                        'range' : [0, self.width]
                    },
                    yaxis={
                        'showline' : False, # hide axis line, grid, ticklabels and  title
                        'zeroline' : False,
                        'showgrid' : False,
                        'showticklabels' : False,
                        'range' : [0, self.height]
                    },         
                    margin=dict(l=0, r=0, b=0, t=30),
                    hovermode='closest',
                    plot_bgcolor=self.plot_bg,
                    paper_bgcolor=self.plot_bg
                    #shapes=shapes,
                    #width=self.width,
                    #height=self.height
                    )
        return layout


    def view(self, **kwargs):
        """View the current state of the tree and save it to the history.

        Kwargs:
            highlight (iterable of Node): some nodes to be highlighted.
        """
        snapshot = self._create_snapshot()
        snapshot['info'] = kwargs
        self.snapshots.append(snapshot)

        # display the new snapshot and enter the event loop
        # start = time.time()
        return self._view(len(self.snapshots) - 1)
    #end_view    

        #self._pause_until_continue()
        # duration = time.time() - start
        # if wait:
        #    self._pause_until_continue()
        # elif pause > duration:
        #    time.sleep(pause - duration)
   

    def _view(self, new_snapshot_index=None):
        
        if new_snapshot_index is None:
            # redraw
            new_snapshot_index = self.current_snapshot_index
            return self.figures[self.current_snapshot_index - 1]
        elif new_snapshot_index - 1 < len(self.figures) and new_snapshot_index > 0:
            self.current_snapshot_index = new_snapshot_index
            return self.figures[self.current_snapshot_index - 1]
        elif new_snapshot_index == self.current_snapshot_index \
                or new_snapshot_index <= 0 \
                or new_snapshot_index >= len(self.snapshots):
            # nothing new
            return self.figures[self.current_snapshot_index - 1]

        #endif

        old_snapshot = self.snapshots[self.current_snapshot_index]
        new_snapshot = self.snapshots[new_snapshot_index]
        self.current_snapshot_index = new_snapshot_index

        node_colors = {}
        node_label_colors = {}
        node_attributes = {}

        for node, (pos, node_dict, attr, shape) in new_snapshot['nodes'].items():

            node_attributes[node] = attr
            try:
                node_colors[node] = node_dict['color']
                node_label_colors[node] = 'white'
            except KeyError:
                node_colors[node] = 'white'
                node_label_colors[node] = 'black'
        #endfor

        def currentPos(node, f):
            # interpolate between old and new pos of a node in new_snapshot
            # where f is in [0..1]
            nx, ny = new_snapshot['nodes'][node][0]
            # scale to window dimensions
            nx *= self.width/new_snapshot['width']
            ny *= self.height/new_snapshot['height']

            if node in old_snapshot['nodes']:
                ox, oy = old_snapshot['nodes'][node][0]
                ox *= self.width/old_snapshot['width']
                oy *= self.height/old_snapshot['height']
            else:
                ox, oy = nx, ny
            #endif

            return (nx*f + ox*(1-f), ny*f + oy*(1-f))
        #end_current_pos

        def create_edges() -> list:
            # EDGES
            edges = []
            for node in new_snapshot['nodes']:
                edge_between_nodes = None
                if node != new_snapshot['root']:
                    # has parent
                    # TODO refactor tango fix
                    color = 'rgb(220,220,220)'
                    width = 1.0
                    to_dash = None
                    if 'is_root' in new_snapshot['nodes'][node][1]:
                        # tango tree quick fix:
                        # highlight preferred paths
                        if new_snapshot['nodes'][node][1]['is_root']:
                            color = 'rgb(220,220,220)'
                            width = 1.0
                            to_dash = "dash"
                        else:
                            color = 'rgb(135,206,250)'
                            width = 3.0
                            to_dash = "solid"
                        #endif
                        #----------------EDGES PATHS FOR TANGO-------------------

                        curr_pos_node = currentPos(node, f) # coords of the current node placement
                        curr_pos_next = currentPos(new_snapshot['nodes'][node][1]['parent'], f) # coords of the destination node
                        edge_between_nodes = dict(
                            x=[curr_pos_node[0], curr_pos_next[0]],
                            y=[curr_pos_node[1], curr_pos_next[1]],
                            name="Preferred path",
                            line={
                                'shape' : 'spline',
                                'color' : color,
                                'dash' : to_dash,
                                'width' : width
                            },
                            mode='lines'
                        )
                        #----------------\EDGES PATHS FOR TANGO-------------------

                    #endif 'is_root' in new_snapshot['nodes'][node][1]
                    else:
                        #----------------EDGES PATHS FOR OTHER-------------------
                        curr_pos_node = currentPos(node, f)
                        curr_pos_next = currentPos(new_snapshot['nodes'][node][1]['parent'], f)

                        edge_between_nodes = dict(
                            x=[curr_pos_node[0], curr_pos_next[0]],
                            y=[curr_pos_node[1], curr_pos_next[1]],
                            name="Edge",
                            line=dict(
                                shape='spline',
                                color=color,
                                dash=to_dash
                            ),
                            mode='lines'
                        )
                        #----------------\EDGES PATHS FOR OTHER-------------------

                    #endelse 'is_root' in new_snapshot['nodes'][node][1]

                #endif node != new_snapshot['root']

                if edge_between_nodes is not None:
                    edges.append(edge_between_nodes)

            #endfor_node
            return edges
        #---end_create_edges-----


        def create_dots() -> list:
            dots = []
            #---------------------------NODES------------------------
            X_nodes_dots = []
            Y_nodes_dots = []

            X_nodes_sq = []
            Y_nodes_sq = []

            annotations = self.make_annotations()

            labels_circle = []
            labels_sq = []

            labels_circle_short = []
            labels_sq_short = []

            circles = 0
            squares = 0

            for node in new_snapshot['nodes']:

                (x, y) = currentPos(node, f)
                shape = new_snapshot['nodes'][node][3]

                if shape is NodeShape.circle:
                    X_nodes_dots += [x]
                    Y_nodes_dots += [y]

                    labels_circle += [new_snapshot['nodes'][node][1]['key']]

                    if labels_circle[circles] > 999:
                        labels_circle_short += ["..."]
                    else:
                        labels_circle_short += [str(labels_circle[circles])]

                    circles += 1

                elif shape is NodeShape.square:
                    X_nodes_sq += [x]
                    Y_nodes_sq += [y]

                    labels_sq += [new_snapshot['nodes'][node][1]['key']]

                    if labels_sq[squares] > 999:
                        labels_sq_short += ["..."]
                    else:
                        labels_sq_short += [str(labels_sq[squares])]

                    squares += 1
                #endif
                # additional info next to node
            #endfor
            nodes_dots = dict(
                        x=X_nodes_dots,
                        y=Y_nodes_dots,
                        mode='markers+text',
                        name='',
                        marker=dict(symbol='circle',
                                size=self.node_radius, 
                                color='rgb(20,255,20)',    #'#DB4551', 
                                line=dict(color='rgb(250,250,250)', 
                                width=1),
                                opacity=0.8
                            ),
                        opacity=1,
                        text=labels_circle_short,
                        hoverinfo='text',
                        hovertext=labels_circle,
                        textfont=dict(
                            size=self.font[1],
                            family=self.font[0],
                            color='rgb(255, 255, 255)'
                            )
                      )

            nodes_squares = dict(
                        x=X_nodes_sq,
                        y=Y_nodes_sq,
                        mode='markers+text',
                        name='',
                        marker=dict(symbol='square',
                                    size=self.node_radius, 
                                    color='rgb(128,128,128)',
                                    line=dict(color='rgb(135,206,250)', 
                                    width=2),
                                    opacity=0.7
                                ),
                        text=labels_sq_short,
                        hoverinfo='text',
                        hovertext=labels_sq,
                        textfont=dict(
                            size=self.font[1],
                            family=self.font[0],
                            color='rgb(255, 255, 255)'
                            )
                      )

            dots.append(nodes_dots)
            dots.append(nodes_squares)
            return dots
            #---------------------------\NODES------------------------

        #---end_create_dots-----


        def create_shapes() -> list:
            # additional info
            # highlight node
            shapes = []
            X = []
            Y = []
            highlight_nodes = new_snapshot['info'].get('highlight_nodes', [])
            arrow_length = 2 * self.node_radius   # TODO setting
            arrow_size = arrow_length / 8
            arrow_color = 'rgb(250, 250, 250)'

            for node in highlight_nodes:

                if node in new_snapshot['nodes']:
                    x, y = currentPos(node, f)
                    shapes.append(
                    {
                        'type': 'line',
                        'x0': x - self.node_radius - arrow_length,
                        'y0': y,
                        'x1': x - self.node_radius,
                        'y1': y,
                        'line': {
                            'width': 1,
                            'color' : arrow_color
                        }
                    })
                    X.append(x - self.node_radius)
                    Y.append(y)

                #endif
            #endfor
            arrows = dict(
                x=X,
                y=Y,
                mode='markers',
                name='',
                marker=dict(symbol='triangle-right',
                            size=arrow_size, 
                            color=arrow_color,
                            line=dict(color=arrow_color, 
                            width=2)
                        )
                )
            return (shapes, arrows)
        #---end_create_shapes-----

        def create_figure(f=1):

            edges = create_edges()
            dots = create_dots()
            shapes, arrows = [], []#create_shapes()
            data = go.Data(edges + dots + [arrows])
            self.figures.append(data)
            #fig = {'data' : data, 'layout' : layout, 'frames' : []}

        #end_create_figure

        f = 1
        create_figure()
        return self.figures[self.current_snapshot_index - 1]
    #end_view

    # TODO view_after redesign
    def _view_after(self, f):
        """Wrap a function f (of a class) to automatically invoke
        self.view(method=f.__name__) after execution.
        """
        # TODO view_after redesign
        # TODO split drawing and observation in different classes
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            res = f(*args, **kwargs)
            self.view(method=f.__name__)
            return res
        wrapper = types.MethodType(wrapper, self.t)
        return wrapper
    #end_view_after

#end_TreeView

if __name__ == '__main__':
    from bstvis.tree.rb import RBTree

    t = RBTree()
    tv = TreeView(t, node_attributes=['bh'],
                  width=1300, height=600, node_radius=12, font_size=12)

    import random
    random.seed(0)

    universe = list(range(20))
    random.shuffle(universe)
    for i in universe:
        t.insert(i)
        tv.view(highlight_nodes=[t.root])
