#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#---------------SYS----------------
import sys
#--------------\SYS----------------

#-----------DASH Modules-----------
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, Event, State
#----------\DASH Modules-----------

#---------------Trees--------------
from tree.naive import *
import tree.tango_strict as tg
from tree.rb import RBNode, RED, BLACK
#--------------\Trees--------------

#---------------Views--------------
import viewer.treeview as treeview
from viewer.treelayout import SimpleBinaryTreeLayout
#---------------\Views-------------

#---------------Rest---------------
import random as rd
#--------------\Rest---------------

#---------------Data---------------
colors = {"bg" : '#323232', 
    "sep" : '#484848',
    "blue" : '#7FDBFF',
    "smoke" : 'F5F5F5',
    "o-red" : 'rgba(255, 0, 0, 0.5)',
    "o-green" : 'rgba(0, 255, 0, 0.5)',
    "black-grey" : '#111111'}

texts = {
    "short-desc" : 'This is a implementation of Tango Trees as described in\
    "Dynamic Optimality - Almost". An O(lg lg n)-competitive online binary search tree, improving upon the\
best previous (trivial) competitive ratio of O(lg n)'
}
PAUSED = True
#--------------\Data---------------

def validate(value):
    if value == '':
        return 1
    result = []
    for i in value:
        try:
            result += [int(i)]
        except Exception as e:
            pass
        else:
            pass
        finally:
            pass
    return result

def validate_input(value_add):
    print(value_add)
    result = []
    for i in value_add:
        try:
            result += [int(i)]
        except Exception as e:
            pass
        else:
            pass
        finally:
            pass
    return result

#------------------------------------------------View--------------------------------------------------
#--------------Header--------------
def create_header():
    header = html.Div(children=[
        html.Div(children=[
            html.Nav(children=[
                html.Div(children=[
                    html.Div(children=[
                        dcc.Link('Tango Tree', href="#", className="navbar-brand navbar-link"),
                        #TODO
                        ]),
                    html.Div(className="fa fa-code-fork", style={'margin-left' : '-230px'}),
                    html.P(children=[
                        dcc.Link('Dash framework', href="https://dash.plot.ly/getting-started", className="navbar-link login"),
                        dcc.Link('GIT', href="https://github.com/StepanTita/bstree-tango", className="btn btn-default action-button")
                        ], className="navbar-text navbar-right")
                    ], className="container")
                ], className="navbar navigation-clean-search"),
            html.Hr(),
            html.Div(children=[
                html.Div(children=[
                    html.Div(children=[
                        html.H1('Tango Trees'),
                        html.P(texts['short-desc']),
                        dcc.Link('Learn more', className='btn btn-default btn-lg action-button', href='http://erikdemaine.org/papers/Tango_SICOMP/paper.pdf')
                        ], className="col-lg-4 col-lg-offset-0 col-md-4 col-md-offset-0"),
                    html.Div(children=[
                        html.Div(children=[
                            html.Img(src="assets/img/treeroot.png", className="device"),
                            #html.Div(className="screen")
                            ], className="iphone-mockup")
                        ], className="col-lg-8 col-lg-offset-0 col-md-8 col-md-offset-0 hidden-xs hidden-sm phone-holder")
                    ], className="row")
                ], className="container hero")
            ], className="header-blue")
        ]
    )
    return header
#-------------\Header--------------

#------------Controls--------------
def create_controls_search():
    controls = html.Div(children=[
        html.Div(children=[
            html.Div(children=[
                dcc.Input(
                    id='search-box',
                    placeholder='Enter a value...',
                    type='text',
                    value='',
                    className='nine columns'
                ),
                html.Button('search', id="search-button", className='three columns'),
                dcc.Checklist(
                    id='vis-all',
                    options=[
                        {'label': 'Visualize all the searches?', 'value': 'vis'}, 
                        {'label': 'Visualize steps?', 'value': 'step'}
                    ],
                    values=['vis', 'step']
                )
                ], className='container', style={'color' : 'white', 'font-size' : '15pt'})
            ], className='row')
    ])
    return controls

def create_controls_add():
    controls = html.Div(children=[
        html.Div(children=[
            dcc.Input(id='add-box', type='text', value='', className='nine columns', placeholder='1...32'),
            html.Button('Add items', id='add-button', className='three columns')
            ], className='container')
        ], className='row', style={'margin-bottom' : '20px', 'margin-top' : '30px', 'font-size' : '15pt'})
    return controls

def create_controls_dropdown():
    controls = html.Div(children=[
        dcc.Dropdown(id='graphs-choise',
                    className='twelve columns',
                    options=[{'label': s, 'value': s} for s in figures.keys()],
                    value=[s for s in figures.keys()],
                    multi=True
                    )
        ], className='container', style={'font-size' : '15pt'})
    return controls

def create_controls_graph():
    controls = html.Div(children=[
        html.Div(children=html.Div(id='graphs'), className='twelve columns', style={
            'margin' : '10px'
            }),
        dcc.Interval(
            id='graph-update',
            interval=1000)
        ], className='row my-graph')
    return controls

def create_controls_slider():
    controls = html.Div(children=[
        html.Div(children=[
            dcc.Slider(
                id='speed-slider',
                min=1,
                max=10,
                step=0.5,
                value=5,
                marks={i: 'Speed {}'.format(i) for i in range(1, 11)}
            )
            ], className='container')
        ], className='row')
    return controls

def create_controls():
    controls = html.Div(children=[
        html.Div(children=[
            html.Button(children=[
                html.Span(className='fa fa-backward')
                    ], className='my-btn', id='prev-button'),
            html.Button(children=[
                html.Span(className='bar bar-1'),
                html.Span(className='bar bar-2')
                    ], className='my-btn play centered', id='pause-button'),
            html.Button(children=[
                html.Span(className='fa fa-forward', id='next-button')
                    ], className='my-btn')
                ], className='my-container d-flex justify-content-between')
        ], className="row moves")
    return controls
#-----------\Controls--------------

#--------------Table---------------
def get_class_name(action):
    danger = 'table-danger'
    default = 'default'
    success = 'table-success'
    info = 'table-info'
    if action == tg.SEARCH_END:
        return danger
    elif action == tg.SEARCH_SUCCESS:
        return success
    elif action == tg.SEARCH_START:
        return info
    else:
        return default

def generate_table(df, max_rows=10):
    counter = 0
    #df.reverse()
    table = html.Table(children=[
        html.Thead(children=[
            html.Tr(children=[
                html.Th('#', scope='col'),
                html.Th('Log', scope='col'),
                html.Th('Time', scope='col')
                ])
            ]),
        html.Tbody(children=[
            html.Tr(children=[
                html.Td(i),
                html.Td(d['text']),
                html.Td(d['time'])
                ], className=get_class_name(d['act'])) for d in df[-max_rows:]
            ])
        ], className='table table-hover table-dark', style={'color' : colors['smoke'], 'margin-top' : '10px', 'font-size' : '13pt'})
    return html.Div(children=[table], className='container', style={ 'max-height' : '500px'})
#-------------\Table---------------

#-----------------------------------------------\View--------------------------------------------------

#----------------App---------------
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', 'https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css', 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css']#'https://codepen.io/amyoshino/pen/jzXypZ.css']#["https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css"]#
external_scripts = ['https://code.jquery.com/jquery-3.3.1.slim.min.js', 'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js', 'https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/js/bootstrap.min.js']#["https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts)
#---------------\App---------------


#----------------TREE--------------
nr_vertices = 8

#naive_bst = pd.ParodyTree()

#for i in range(nr_vertices):
#    new_value = rd.randint(1, 100)
#    naive_bst.insert(new_value)
#endfor

#res = []
#print("START")
tango_bst = tg.TangoTree(range(1, 16))
naive_bst = tango_bst.parody
#tango_bst.search(9)
#tango_bst.search(15)
#tango_bst.search(3)
for i in range(100):
    val = rd.randint(1, 15)
    #res += [val]
    #tango_bst.search(val)
#print("END")
#print(res)
tango_view = treeview.TreeView(tango_bst,
                  node_attributes=['d', 'min_d', 'max_d'],
                  node_shape=tg.node_shape, plot_bg=colors['black-grey'])
naive_view = treeview.TreeView(tree=naive_bst, layout_algorithm=SimpleBinaryTreeLayout, plot_bg=colors['black-grey'])

figures = {
    'Perfectly balanced binary search tree' : dict(data=naive_view.view(), layout=naive_view.create_layout()),
    'Auxilary trees' : dict(data=tango_view.view(), layout=tango_view.create_layout())
    }

#-----------------------------------------------------------------------------------------------------------------

app.config['suppress_callback_exceptions'] = True
app.layout = html.Div(children=[
    create_header(),
    html.Hr(),
    html.H1("Layout tango binary search tree", className='text-center'),
    create_controls_add(),
    create_controls_dropdown(),
    create_controls_graph(),
    create_controls(),
    create_controls_slider(),
    html.Div(children=[
        html.Div(children=[
            html.H1('Log of operations'),
            generate_table(tango_bst.search_log)
            ], className='six columns', id='table-container'),
        html.Div(children=[
            html.H1('Search value'),
            create_controls_search()
            ], className='six columns')
        ], className='row', style={'margin-bottom' : 0}),
    html.Div(id='hidden-div', style={'display':'none'})
], className="main-div")

#-------------CallBacks-----------

def next_update():
    figures['Auxilary trees']['data'] = tango_view.next_callback()
    figures['Perfectly balanced binary search tree']['data'] = naive_view.next_callback()

def prev_update():
    figures['Auxilary trees']['data'] = tango_view.previous_callback()
    figures['Perfectly balanced binary search tree']['data'] = naive_view.previous_callback()

def dropdown_update(data_names):
    if len(data_names) > 1:
        class_choice = 'six columns'
    else:
        class_choice = 'twelve columns'
    graphs = []
    for data_name in data_names:
        graphs.append(html.Div(dcc.Graph(
                id=data_name,
                figure=figures[data_name],
                animate=True,
                animation_options=dict(
                    transition={'duration' : 500},
                    redraw=False
                )
            ), className=class_choice, style={'border' : 'solid', 'border-color' : colors['blue'], 'border-width' : '1px'}))
    return graphs

def build_tree(keys):
    global tango_bst
    global tango_view
    global naive_bst
    global naive_view
    tango_bst = tg.TangoTree(keys)
    tango_view = treeview.TreeView(tango_bst,
                  node_attributes=['d', 'min_d', 'max_d'],
                  node_shape=tg.node_shape, plot_bg=colors['black-grey'])
    naive_bst = tango_bst.parody
    naive_view = treeview.TreeView(tree=naive_bst, layout_algorithm=SimpleBinaryTreeLayout, plot_bg=colors['black-grey'])
    figures['Auxilary trees'] = dict(data=tango_view.view(), layout=tango_view.create_layout())
    figures['Perfectly balanced binary search tree']['data'] = dict(data=naive_view.view(), layout=naive_view.create_layout())

clicks = {
    'search' : None,
    'next' : None,
    'prev' : None, 
    'add' : None
}

@app.callback(
    dash.dependencies.Output('graph-update', 'interval'),
    [dash.dependencies.Input('speed-slider', 'value')])
def update_speed(value):
    return value * 1000

@app.callback(
    dash.dependencies.Output('table-container', 'children'),
    [dash.dependencies.Input('search-button', 'n_clicks')])
def update_table(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        return [html.H1('Log of operations'),
                generate_table(tango_bst.search_log)]

@app.callback(
    dash.dependencies.Output('hidden-div', 'value'),
    [dash.dependencies.Input('pause-button', 'n_clicks')])
def update_pause(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        global PAUSED
        PAUSED = not PAUSED
    return ''

@app.callback(
    dash.dependencies.Output('Auxilary trees', 'animation_options'),
    [dash.dependencies.Input('speed-slider', 'value')])
def update_output(value):
    return dict(frame=dict(duration=value * 1000, redraw=False), transition={'duration' : value * 1000})

@app.callback(
    dash.dependencies.Output('Layout tango binary search tree', 'animation_options'),
    [dash.dependencies.Input('speed-slider', 'value')])
def update_output(value):
    return dict(frame=dict(duration=value * 1000, redraw=False), transition={'duration' : value * 1000})

@app.callback(
    Output('hidden-div','placeholder'),
    [Input('search-button', 'n_clicks'),
    Input('vis-all', 'values')],
    [State('search-box', 'value')])
def search_update(n_clicks, checked, value):
    print(checked)
    prev_snapshot_t = tango_view.current_snapshot_index
    prev_snapshot_n = naive_view.current_snapshot_index
    if n_clicks != clicks['search']:
        if 'step' not in checked:
            tango_bst.step = False
        elif 'step' in checked:
            tango_bst.step = True
        value = validate(value.split(','))
        for i in value:
            tango_bst.search(i)
            if 'vis' in checked:
                tango_view.view()
                naive_bst.view()
    tango_view.current_snapshot_index = prev_snapshot_t
    naive_view.current_snapshot_index = prev_snapshot_n
    #figures['Auxilary trees']['data'] = tango_view.view()

@app.callback(
    Output('graphs','children'),
    [Input('graphs-choise', 'value'),
    Input('next-button', 'n_clicks'),
    Input('prev-button', 'n_clicks'),
    Input('add-button', 'n_clicks')],
    [State('add-box', 'value')],
    events=[dash.dependencies.Event('graph-update', 'interval')]
    )
def update_graph(data_names, n_clicks_next=0, n_clicks_prev=0, n_clicks_add=0, value_add=1):
    global PAUSED
    if n_clicks_next != clicks['next']:
        next_update()
        clicks['next'] = n_clicks_next
        PAUSED = True
    elif n_clicks_prev != clicks['prev']:
        prev_update()
        clicks['prev'] = n_clicks_prev
        PAUSED = True
    elif clicks['add'] != n_clicks_add:
        if '...' in value_add:
            my_range = validate_input(value_add.split('...'))
            try:
                build_tree(range(my_range[0], my_range[1]))
            except Exception as e:
                pass
        elif ',' in value_add:
            my_range = validate_input(value_add.split(','))
            if len(my_range) > 0:
                build_tree(my_range)
        clicks['add'] = n_clicks_add
        PAUSED = True
    if not PAUSED:
        next_update()

    graphs = dropdown_update(data_names)
    return graphs

if __name__ == '__main__':
    app.run_server(debug=True)
