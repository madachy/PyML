"""
PyML Version .19

Copyright (c) 2022 Ray Madachy

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import graphviz
import textwrap
import os
import sys
from os.path import exists
import pandas as pd
from copy import deepcopy

# text for SVG included files

actor_svg = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   version="1.1"
   width="50"
   height="100"
   stroke-linecap="round"
   stroke-linejoin="round"
   id="svg30"
   sodipodi:docname="actor.svg"
   inkscape:version="1.0.1 (3bc2e813f5, 2020-09-07)">
  <metadata
     id="metadata36">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title />
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <defs
     id="defs34" />
  <sodipodi:namedview
     pagecolor="#ffffff"
     bordercolor="#666666"
     borderopacity="1"
     objecttolerance="10"
     gridtolerance="10"
     guidetolerance="10"
     inkscape:pageopacity="0"
     inkscape:pageshadow="2"
     inkscape:window-width="2513"
     inkscape:window-height="1533"
     id="namedview32"
     showgrid="false"
     inkscape:zoom="8.5843373"
     inkscape:cx="1.4561402"
     inkscape:cy="58"
     inkscape:window-x="535"
     inkscape:window-y="435"
     inkscape:window-maximized="0"
     inkscape:current-layer="svg30"
     inkscape:document-rotation="0" />
  <g
     transform="matrix(0.68481344,0,0,0.83385173,-228.58233,-393.63174)"
     style="fill:none;stroke:#000000;stroke-width:2.64666px"
     id="g28">
    <path
       d="m 91.166271,19.719835 a 13.195118,13.068849 0 1 1 -26.390236,0 13.195118,13.068849 0 1 1 26.390236,0 z"
       transform="matrix(1.131591,0,0,1.1425243,281.27172,471.26198)"
       id="path24"
       style="stroke-width:2.64666px" />
    <path
       d="m 77.497641,34.903691 v 46.056642 m 0,-0.56821 -19.445437,16.541248 M 77.529208,80.392123 98.868681,95.860084 M 57.073619,47.49903 98.931815,47.46746"
       transform="translate(292,474.36218)"
       id="path26"
       style="stroke-width:2.64666px" />
  </g>
</svg>"""

def context_diagram(system, external_systems, filename=None, format='svg', engine='neato'):
    """
    Returns a context diagram.

    Parameters
    ----------
    system_name : string
        The name of the system to label the diagram.
    external_systems : list of strings
        Names of the external systems that interact with the system in a list.
    filename : string, optional
        A filename for the output not including a filename extension. The extension will specified by the format parameter.
    format : string, optional
        The file format of the graphic output. Note that bitmap formats (png, bmp, or jpeg) will not be as sharp as the default svg vector format and most particularly when magnified.

    Returns
    -------
    g : graph object view
        Save the graph source code to file, and open the rendered result in its default viewing application. PyML calls the Graphviz API for this.

    """
    wrap_width = 20
    def wrap(text): return textwrap.fill(
        text, width=wrap_width, break_long_words=False)
    node_attr = {'color': 'black', 'fontsize': '11', 'fontname': 'arial',
                 'shape': 'box'}  # 'fontname': 'arial',
    c = graphviz.Graph('G', node_attr=node_attr,
                       filename=filename, format=format, engine=engine)

    human_actor_keywords = ["User", "user", "Customer", "customer", "Operator", "Patient", "Doctor", "operator"]

    for external_system in external_systems:
        if (external_system in human_actor_keywords): c.node(wrap(external_system), labelloc="b", image='actor.svg', shape='none')
        c.edge(wrap(system), wrap(external_system), len="1.2") # len="1.2"
    if filename is not None:
        c.render()  # render and save file, clean up temporary dot source file (no extension) after successful rendering with (cleanup=True) doesn't work on windows "permission denied"
    return c


def activity_diagram(element_dependencies, filename=None, format='svg'):
    node_attr = {'color': 'black', 'fontsize': '11',
                 'style': "rounded", 'shape': 'box'}  # 'fontname': 'arial',
    edge_attr = {'arrowsize': '.5', 'fontname': 'arial', 'fontsize': '11', }
    activity = graphviz.Digraph('G', filename=filename, node_attr=node_attr,
                                edge_attr=edge_attr, engine="dot", format=format)
    activity.attr(rankdir='LR',)
    activity.edges(element_dependencies)

    if filename != None:
        activity.render()  # render and save file, clean up temporary dot source file (no extension) after successful rendering with (cleanup=True) doesn't work on windows "permission denied"
        #os.remove(filename) also doesn't work on windows "permission denied"
    return activity


def use_case_diagram(system_name, actors, use_cases, interactions, use_case_relationships, filename=None, format='svg'):
    """ Draw a use case diagram.

    Parameters
    ----------
    system_name : string
        The name of the system to label the diagram.
    actors : list of strings
        Names of the outside actors that interact with the system in the use cases in a list.
    use_cases : list of strings
        Names of the use cases in a list.
    interactions : list of tuples
        A list of the interactions to be drawn between actors and use cases. Each interaction is a tuple containing an actor and use case in the form ("actor name", "use case name") indicating an arrow drawn from the actor to the use case. Interactions are graph edges.
    use_case_relationships : list of tuples, optional
        A list of the relationships, or associations to be drawn between use cases. Each relationship is a tuple containing a use case pair and type relationship in the form ("use case 1", "use case 2", "relationship") indicating an arrow drawn from the first to the second use case. Relationship types are "<<include>>", "<<extend>>" and "generalization".
    filename : string, optional
        A filename for the output not including a filename extension. The extension will specified by the format parameter.
    format : string, optional
        The file format of the graphic output. Note that bitmap formats (png, bmp, or jpeg) will not be as sharp as the default svg vector format and most particularly when magnified.

    Returns
    -------
    g : graph object view
        Save the graph source code to file, and open the rendered result in its default viewing application. PyML calls the Graphviz API for this.

    """
    wrap_width = 15
    def wrap(text): return textwrap.fill(
        text, width=wrap_width, break_long_words=False)
    node_attr = {'color': 'black', 'fontname': 'arial',
                 'fontsize': '11',  'width': '0.'}
    edge_attr = {'arrowsize': '.5', 'fontname': 'arial', 'fontsize': '11', }
    u = graphviz.Digraph('G', filename=filename, node_attr=node_attr,
                         edge_attr=edge_attr, engine="neato", format=format)
    system_height = len(use_cases) + .5

    u.node(system_name, label=f'''<<b>{system_name}</b>>''', pos=f'0,{(system_height+.5)/2}!',
           shape="box", height=f"{system_height}", width="2", labelloc="t")

    if exists("actor.svg") == False:
        a = open("actor.svg", "w")
        a.write(actor_svg)
        a.close()

    column = -2
    for number, actor in enumerate(actors):
        division = system_height / (len(actors) + 1)
        #print (division)
        u.node(wrap(actor), pos=f'{column}, {system_height - division*(number+1) + .25}!',
               width='.1', shape='none', image='actor.svg', labelloc='b')

    column = 0
    for number, use_case in enumerate(use_cases):
        u.node(
            wrap(use_case), pos=f'{column}, {len(use_cases)-number}!', width='1.25', height=".7")

    for edge in (interactions):
        u.edge(wrap(edge[0]), wrap(edge[1]))  # lhead='clusterx' not used

    if filename != None:
        u.render()  # render and save file, clean up temporary dot source file (no extension) after successful rendering with (cleanup=True) doesn't work on windows "permission denied"
        #os.remove(filename) also doesn't work on windows "permission denied"
    return u


def sequence_diagram(system_name, actors, objects, actions, filename=None, format='svg'):
    """ Returns a sequence diagram.

    Parameters
    ----------
    system_name : string
        The name of the system to label the diagram.
    actors : list of strings
        Names of the outside actors that participate in the activity sequence in a list.
    objects : list of strings
        Names of the system objects that participate in the activity sequence in a list.
    actions : list of tuples
        A chronologically ordered list describing the sequence of actions to be drawn. Each action is a tuple containing the action source, target and action name (or data/control passed) in the form ("source", "target", "action name") indicating a labeled horizontal arrow drawn between them.
    filename : string, optional
        A filename for the output not including a filename extension. The extension will specified by the format parameter.
    format : string, optional
        The file format of the graphic output. Note that bitmap formats (png, bmp, or jpeg) will not be as sharp as the default svg vector format and most particularly when magnified.

    Returns
    -------
    g : graph object view
        Save the graph source code to file, and open the rendered result in its default viewing application. PyML calls the Graphviz API for this.

    """
    verbose = False
    wrap_width = 40
    def wrap(text): return textwrap.fill(
        text, width=wrap_width, break_long_words=False)
    graph_attr = {'rankdir': 'LR', 'color': 'black'}
    node_attr = {'shape': 'point', 'color': 'none',
                 'fontname': 'arial', 'fontsize': '11',  'width': '0.'}
    edge_attr = {'arrowsize': '.5', 'fontname': 'arial', 'fontsize': '11', }
    g = graphviz.Digraph('G', filename=filename, graph_attr=graph_attr,
                         node_attr=node_attr, edge_attr=edge_attr, engine="neato", format=format)

    if exists("actor.svg") == False:
        a = open("actor.svg", "w")
        a.write(actor_svg)
        a.close()

    # spread actors/objects apart on x-axis, differentiate actors from objects for images used
    object_spacing = 3
    object_x_coords = {}  # dictionary holds x coordinates for action nodes and edges
    for actor_object_number, actor_object in enumerate(actors+objects, start=1):
        x = int(actor_object_number-1)*object_spacing
        if actor_object in actors:
            g.node(actor_object, pos=f"{x},.2!",
                   shape="none", image='actor.svg', labelloc='b')
        if actor_object in objects:
            g.node(actor_object, pos=f"{x},.2!", shape="box", color='black')
        object_x_coords[actor_object] = x

    # create nodes for each action source and destination to draw arrows to/from
    # must capture last action # to draw lifelines to
    object_last_actions = {}  # dictionary holds last action for objects and actors

    for action_number, action in enumerate(actions, start=1):
        for actor_object, x in object_x_coords.items():
            y = int(action_number)*.4
            if action[0] == actor_object:
                # arrow node names: actor/object  action #
                g.node(f'{action[0]} {int(action_number)}', pos=f"{x},-{y}!")
            if action[1] == actor_object:
                g.node(f'{action[1]} {int(action_number)}', pos=f"{x},-{y}!")
            if actor_object == action[0] or actor_object == action[1]:
                object_last_actions[actor_object] = action_number
            if verbose:
                print(
                    actor_object, f'{action[0]}->{action[1]} # {int(action_number)}', f"pos {x},-{y}!")

    # edges for each arrow going down
    for action_number, action in enumerate(actions, start=1):
        source_x, target_x = object_x_coords[action[0]
                                             ], object_x_coords[action[1]]
        g.edge(f'{action[0]} {int(action_number)}', f'{action[1]} {int(action_number)}',  headlabel=f'{wrap(action[2]) if len(action[2]) > wrap_width else action[2]}', labeldistance=str(
            object_spacing * 3.6), labelangle=f'{-5 if source_x < target_x else 5}')  # left to right -10 with x separation = 1 wrap = 25 .5 y,  right to left 15 with x separation = 1 wrap = 25 .5y

    # lifelines
    for actor_object in actors+objects:
        if verbose:
            print(actor_object, f'{actor_object} {len(actions)}')
        g.edge(
            actor_object, f'{actor_object} {object_last_actions[actor_object]}', style='dashed', arrowhead='none')

    if verbose:
        print(object_x_coords)
    if verbose:
        print(object_last_actions)
    if filename != None:
        g.render()  # render and save file, clean up temporary dot source file (no extension) after successful rendering with (cleanup=True) doesn't work on windows "permission denied"
        #os.remove(filename) also doesn't work on windows "permission denied"
    return g


def design_structure_matrix(elements, element_dependencies, filename=None, format='svg'):
    """
    Draw a design structure matrix of system elements and their dependencies. Matrix elements may represent tasks (process activities), system parameters or attributes.

    Parameters
    ----------
    elements : list of strings
        Names of the matrix elements as the row and column headings in a list.
    element_dependencies : list of tuples
        A list of tuples describing the relationships between elements. Each relationship is a tuple containing the relationship input element, output element and optionally a custom label (or other object) to mark the relationship in the form ("input element", "output element", "relationship label"). The default marking denoting a relationship is an uppercase 'X', therefore, the shortened tuple relationship ("input element", "output element") is equivalent to ("input element", "output element", "X"). A custom label can be specified as html code for styling of the font type, font color, cell color, etc. Images and unicode characters can be inserted this way, or other html markup for lists, tables, etc.
    filename : string, optional
        A filename for the output not including a filename extension. The extension will specified by the format parameter.
    format : string, optional
        The file format of the graphic output. Note that bitmap formats (png, bmp, or jpeg) will not be as sharp as the default svg vector format and most particularly when magnified.

    Returns
    -------
    g : graph object view
        The rendered graph for display. It will be automatically displayed in Jupyter Notebooks or IPython consoles. With other Python editors it can be displayed in the associated console by typing the returned graph name (e.g., call the function with an assignment such as ``dsm = design_structure_matrix(...)`` and then type ``dsm`` in the console). If a filename is optionally provided, the rendered graph will also be saved as a file in the specified format. PyML calls the Graphviz API for this.

    """
    cell_width = 20  # pixels

    dependency_elements = [dependency[0:2]
                           for dependency in element_dependencies]

    node_string = '<table border="0" cellborder="1"  cellspacing="0">'
    for row, element in enumerate((['']+elements)):
        node_string += '<tr>'
        if row == 0:
            for column, element in enumerate((['']+elements)):
                node_string += f'<td height="{cell_width}px" width="{cell_width}px">' + \
                    element + '</td>'
        else:
            for column, element in enumerate((['']+elements)):
                if column > 0:
                    if row == column:
                        node_string += '<td bgcolor="black"></td>'
                    else:
                        cell_dependency_tuple = (
                            elements[column-1], elements[row-1])  # e.g. ('B', 'A')
                        if cell_dependency_tuple in dependency_elements:
                            if len(element_dependencies[dependency_elements.index(cell_dependency_tuple)]) == 2:
                                # default 'X' label
                                node_string += f'<td height="{cell_width}px" width="{cell_width}px">' + 'X' + '</td>'
                            if len(element_dependencies[dependency_elements.index(cell_dependency_tuple)]) != 2:
                                node_string += f'<td height="{cell_width}px" width="{cell_width}px">' + element_dependencies[dependency_elements.index(
                                    cell_dependency_tuple)][2] + '</td>'  # custom label
                            # print('<td height="{cell_width}px" width="{cell_width}px">', row, column, '</td>')
                        else:
                            node_string += f'<td height="{cell_width}px" width="{cell_width}px">' + '' + '</td>'
                else:
                    node_string += f'<td height="{cell_width}px" width="{cell_width}px">' + \
                        elements[row-1] + '</td>'
        node_string += '</tr>'
    node_string += '</table>'

    dsm = graphviz.Digraph('dsm', filename=filename,
                           format=format, node_attr={'shape': 'plaintext'})
    dsm.node('dsm', f'''<{node_string}>''')
    #dsm.view()
    if filename != None:
        dsm.render()  # render and save file, clean up temporary dot source file (no extension) after successful rendering with (cleanup=True) doesn't work on windows "permission denied"
        #os.remove(filename) also doesn't work on windows "permission denied"
    return dsm


def wbs_diagram(decompositions, filename=None, format='svg', rankdir='TB'):
    """
    Draw a work breakdown structure as a tree hierarchy. Decompositions describe the parent-child relationships.

    Parameters
    ----------
    decompositions : list of tuples
        A list of tuples describing the work decomposition relationships. Each relationship is a tuple containing the parent element followed by the child element.
    filename : string, optional
        A filename for the output not including a filename extension. The extension will specified by the format parameter.
    format : string, optional
        The file format of the graphic output. Note that bitmap formats (png, bmp, or jpeg) will not be as sharp as the default svg vector format and most particularly when magnified.
    rankdir : string, optional
        The direction to display the tree from the parent node. The default ``rankdir='TB'`` denotes top to bottom for a vertical tree decomposition. It can diagrammed horizontally by providing rankdir='LR' to designate left to right.

    Returns
    -------
    g : graph object view
        The rendered graph for display. It will be automatically displayed in Jupyter Notebooks or IPython consoles. With other Python editors it can be displayed in the associated console by typing the returned graph name (e.g., call the function with an assignment such as ``wbs = wbs_diagram(...)`` and then type ``wbs`` in the console). If a filename is optionally provided, the rendered graph will also be saved as a file in the specified format. PyML calls the Graphviz API for this.

    """
    node_attr = {'color': 'black', 'fontsize': '11',
                 'shape': 'box'}  # 'fontname': 'arial',
    edge_attr = {'arrowsize': '.5', 'fontname': 'arial', 'fontsize': '11', }
    activity = graphviz.Digraph('G', filename=filename, node_attr=node_attr,
                                edge_attr=edge_attr, engine="dot", format='svg')
    activity.attr(rankdir=rankdir, splines='ortho')  # rankdir='LR'
    activity.edges(decompositions)

    if filename != None:
        activity.render()  # render and save file, clean up temporary dot source file (no extension) after successful rendering with (cleanup=True) doesn't work on windows "permission denied"
        #os.remove(filename) also doesn't work on windows "permission denied"
    return activity


def tree(element_dependencies, filename=None, format='svg'):
    node_attr = {'color': 'black', 'fontsize': '11',
                 'shape': 'box'}  # 'fontname': 'arial',
    edge_attr = {'arrowsize': '.5', 'fontname': 'arial', 'fontsize': '11', }
    activity = graphviz.Digraph('G', filename=filename, node_attr=node_attr,
                                edge_attr=edge_attr, engine="dot", format='svg')
    activity.attr(rankdir='TB', splines='ortho')  # rankdir='LR'
    activity.edges(element_dependencies)

    if filename != None:
        activity.render()  # render and save file, clean up temporary dot source file (no extension) after successful rendering with (cleanup=True) doesn't work on windows "permission denied"
        #os.remove(filename) also doesn't work on windows "permission denied"
    return activity




def fault_tree_diagram(ft, filename=None, format='svg'):
    """ Returns a fault tree diagram.

    Parameters
    ----------
    ft : list of tuples
        A list of the faults as a tree hierarchy. Each fault is defined in a tuple containing the fault name, type, and underlying faults (if any) in the form
        ``("fault name", "fault name", list of fault branches)``
        with the branches as a list in the form
        ``["branch 1 name", "branch 2 name", ... "branch n name"]``
        to identify the adjoining faults. All basic events will have a blank list
        ``[]`` since they are the bottom leaves in the tree.

        The top event must be in the first row, but all other events can be in any order. They may begrouped by their event paths or by hierarchical levels as convenient. Event types can be conditional "and"s, conditional "or"s, or basic events (leaves). The following spellings are recognized as valid designations for event types:

        And: "And" "and" "AND" \n
        Or: "Or" "or" "OR" \n
        Basic: "Basic" "basic" "BASIC"

    filename : string, optional
        A filename for the output not including a filename extension. The extension will specified by the format parameter.
    format : string, optional
        The file format of the graphic output. Note that bitmap formats (png, bmp, or jpeg) will not be as sharp as the default svg vector format and most particularly when magnified.

    Returns
    -------
    g : graph object view
        Save the graph source code to file, and open the rendered result in its default viewing application. PyML calls the Graphviz API for this.

    """
    verbose = False
    wrap_width = 15
    def wrap(text): return textwrap.fill(
        text, width=wrap_width, break_long_words=False).replace("\n", "<BR/>")
    node_attr = {'color': 'black', 'fontsize': '11',
                 'shape': 'plaintext'}  # 'fontname': 'arial',
    edge_attr = {'arrowtail': 'none', 'arrowsize': '0', 'dir': 'both', 'penwidth': '2', 'fontname': 'arial', 'fontsize': '11', } #https://graphviz.org/docs/attr-types/arrowType/
    fault_tree = graphviz.Digraph('G', filename=filename, node_attr=node_attr,
                                edge_attr=edge_attr, engine="dot", format=format)
    fault_tree.attr(rankdir='TB', splines='line',  ) # polyline


    # create required SVG included files

    and_node = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   width="50"
   height="45"
   transform="rotate(0) translate(0,0)"
   version="1.1"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
  <path
     fill="none"
     stroke="#000000"
     stroke-width="2.61613"
     d="M 24.909933,5.0655629 V 0.01801368"
     id="top_connector" />
  <path
     d="M 5.0927534,45.391608 H 45.092753 v -20.47619 c 0,-11.267907 -9.000045,-19.9999995 -20,-19.9999995 -10.999955,0 -19.9999997,8.7320915 -19.9999997,19.9999995 z m 2.857143,-2.857143 V 24.915418 c 0,-9.760663 7.6399546,-16.6666664 17.1428566,-16.6666664 9.502902,0 17.142857,7.3821944 17.142857,17.1428564 v 17.142857 z"
     id="and_symbol" />
</svg>"""

    or_node = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   width="50"
   height="52"
   version="1.1"
   xmlns="http://www.w3.org/2000/svg">
   <g transform="translate(-22.95,2.65)">
    <path
       fill="none"
       stroke="#000000"
       stroke-width="2.5"
       d="M 48.32812,4.1093798 48.328126,-3 m -6e-6,52.95376 V 43.305394 40.81263"
       id="connectors" />
    <path
       fill-rule="evenodd"
       d="m 28.32812,49.23438 2.4375,-2 c 0,0 7.000049,-5.65625 17.5625,-5.65625 10.562451,0 17.5625,5.65625 17.5625,5.65625 l 2.4375,2 V 32.07813 c 10e-7,-2.408076 0.02451,-7.689699 -2.40625,-13.625 C 63.491106,12.517829 58.578604,5.9165938 49.04687,0.76562982 L 48.32812,2.0781298 47.60937,0.76562982 C 28.54371,11.068743 28.32812,27.321556 28.32812,32.07813 Z m 3,-5.875 V 32.07813 c 0,-4.684173 -0.130207,-18.28685 17,-27.9687502 8.429075,4.766786 12.68391,10.5212812 14.8125,15.7187502 2.195424,5.360661 2.187501,9.841925 2.1875,12.25 v 11.25 c -3.108434,-1.873588 -9.04935,-4.75 -17,-4.75 -7.973354,0 -13.900185,2.908531 -17,4.78125 z"
       id="path382" />
   </g>
 </svg>"""

    or_node_bottom = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   width="50"
   height="49"
   version="1.1"
   xmlns="http://www.w3.org/2000/svg">
   <g transform="translate(-22.95,0.3)">
     <line x1="48.35" x2="48.35" y1="0" y2="3" stroke="black" stroke-width="2.5"/>
   </g>
 </svg>"""

    f3 = open("AND_node.svg", "w")
    f3.write(and_node)
    f3.close()

    f2 = open("OR_node.svg", "w")
    f2.write(or_node)
    f2.close()

    f1 = open("OR_node_bottom.svg", "w")
    f1.write(or_node_bottom)
    f1.close()

    for node in ft:
        node_name, node_type, leafs = node[0], node[1], node[2]
        if verbose: print(f'{node[2]=} {node_name=}, {node_type=} {leafs=}')
        #fault_tree.node(row[0], row[0]+' '+row[1])
        if node_type == "basic" or node_type == "Basic" or node_type == "BASIC":
            fault_tree.node(node_name, f'''<
            <table border="0" cellborder="0" cellspacing="0" cellpadding="0">
              <tr>
            <td >
            <table border="0" cellborder="1" cellspacing="0" cellpadding="0">
              <tr><td port="top">{wrap(node_name)}</td></tr>
            </table>
            </td>
              </tr>
              <tr>
                <td port="{node_type}"></td>
              </tr>
              <tr>
                <td></td>
              </tr>
            </table>>''')
        if node_type == "or" or node_type == "Or" or node_type == "OR":
            fault_tree.node(node_name, f'''<
            <table border="0" cellborder="0" cellspacing="0" cellpadding="0">
              <tr>
            <td >
            <table border="0" cellborder="1" cellspacing="0" cellpadding="0">
              <tr><td port="top">{wrap(node_name)}</td></tr>
            </table>
            </td>
              </tr>
              <tr>
                <td port="{node_type}"><img src="OR_node.svg"/></td>
              </tr>
              <tr>
                <td><img src="OR_node_bottom.svg"/></td>
              </tr>
            </table>>''')
        if node_type == "and" or node_type == "And" or node_type == "AND":
            fault_tree.node(node_name, f'''<
            <table border="0" cellborder="0" cellspacing="0" cellpadding="0">
              <tr>
            <td >
            <table border="0" cellborder="1" cellspacing="0" cellpadding="0">
              <tr><td port="top">{wrap(node_name)}</td></tr>
            </table>
            </td>
              </tr>
              <tr>
                <td port="{node_type}"><img src="AND_node.svg"/></td>
              </tr>
              <tr>
                <td><img src="OR_node_bottom.svg"/></td>
              </tr>
            </table>>''')
        if verbose: print("Leaves")
        for leaf in leafs:
            if verbose: print(node_name,'->', leaf)
            if leaf != '':fault_tree.edge(node_name+':'+node_type+':s', leaf+':top:n') # leaf+':top:n' closer but not symmetrical

    if filename != None:
        fault_tree.render()

    return fault_tree

def read_fault_tree_excel(filename):
    df = pd.read_excel(filename,
            index_col=0,            # the first column contains the index labels (numbers assigned otherwise)
            # skipfooter=2,           # ignore the last two lines of the sheet
            #header=0,               # take the column names from the second row
            #usecols='A:S',          # use these Excel columns
            #sheet_name='Sheet1'  # take data from this sheet
            )
    df = df.fillna('') # replace NaNs to blanks

    fault_tree_list_of_lists = []
    for index in df.index:
         fault_tree_list_of_lists.append([index, df['Type'][index], [df['Branch 1'][index], df['Branch 2'][index], df['Branch 3'][index], df['Branch 4'][index], df['Branch 5'][index], df['Branch 6'][index]], ])
    for event in fault_tree_list_of_lists:
        event[2] = [branch for branch in event[2] if branch !=''] # delete blank fields

    # convert each event list to tuple
    fault_tree_list = [tuple(event) for event in fault_tree_list_of_lists]
    return fault_tree_list

"""
2013.3.12 CKS

A simple critical path method implementation.

http://en.wikipedia.org/wiki/Critical_path_method

To run a unittest:

    python criticalpath.py Test.test_model

"""

PY3 = sys.version_info[0] >= 3
if PY3:
    def cmp(a, b):
        return (a > b) - (a < b)
    # mixin class for Python3 supporting __cmp__

    class PY3__cmp__:
        def __eq__(self, other):
            return self.__cmp__(other) == 0

        def __ne__(self, other):
            return self.__cmp__(other) != 0

        def __gt__(self, other):
            return self.__cmp__(other) > 0

        def __lt__(self, other):
            return self.__cmp__(other) < 0

        def __ge__(self, other):
            return self.__cmp__(other) >= 0

        def __le__(self, other):
            return self.__cmp__(other) <= 0
else:
    class PY3__cmp__:
        pass


# https://codereview.stackexchange.com/a/86067
def cyclic(graph):
    """
    Return True if the directed graph has a cycle.
    The graph must be represented as a dictionary mapping vertices to
    iterables of neighbouring vertices. For example:

    >>> cyclic({1: (2,), 2: (3,), 3: (1,)})
    True
    >>> cyclic({1: (2,), 2: (3,), 3: (4,)})
    False

    """
    visited = set()
    path = [object()]
    path_set = set(path)
    stack = [iter(graph)]
    i = 0
    while stack:
        for v in stack[-1]:
            if v in path_set:
                return True
            elif v not in visited:
                visited.add(v)
                path.append(v)
                path_set.add(v)
                stack.append(iter(graph.get(v, ())))
                break
        else:
            path_set.remove(path.pop())
            stack.pop()
    return False


class Node(object):
    """
    Represents a task in a action precedence network.

    Nodes can be linked together or grouped under a parent node as child nodes.
    """

    def __init__(self, name, duration=None, lag=0):

        self.parent = None

        # A unique identifier of this task.
        self.name = name

        self.description = None

        # How long this task takes to complete.
        self._duration = duration

        # The amount of time the task must wait after the preceeding task
        # has finished before beginning.
        self._lag = lag  # TODO

        self.drag = None  # TODO

        # Earliest start time.
        self._es = None

        # Earliest finish time.
        self._ef = None

        # Latest start time.
        self._ls = None

        # Latest finish time.
        self._lf = None

        # The amount time that the activity can be delayed without
        # changing the start of any other activity.
        self._free_float = None  # TODO

        # The amount of time that the activity can be delayed without
        # increasing the overall project's duration.
        self._total_float = None  # TODO

        self.nodes = []  # set()
        self.name_to_node = {}
        self.to_nodes = set()
        self.incoming_nodes = set()

        self.forward_pending = set()
        self.backward_pending = []

        self._critical_path = None

        self.exit_node = None

    def lookup_node(self, name):
        return self.name_to_node[name]

    def get_or_create_node(self, name, **kwargs):
        try:
            return self.lookup_node(name=name)
        except KeyError:
            n = Node(name=name, **kwargs)
            self.add(n)
            return n

    @property
    def lag(self):
        return self._lag

    @lag.setter
    def lag(self, v):
        self._lag = v

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, v):
        """
        This should only be set by update_all() after calculating
        the critical path of all child nodes.
        """
        self._duration = v

    @property
    def es(self):
        return self._es

    @es.setter
    def es(self, v):
        self._es = v
        if self.parent:
            self.parent.forward_pending.add(self)

    @property
    def ef(self):
        return self._ef

    @ef.setter
    def ef(self, v):
        self._ef = v

    @property
    def ls(self):
        return self._ls

    @ls.setter
    def ls(self, v):
        self._ls = v

    @property
    def lf(self):
        return self._lf

    @lf.setter
    def lf(self, v):
        self._lf = v

    def __repr__(self):
        return str(self.name)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.name == other.name

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __cmp__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return cmp(self.name, other.name)

    def add(self, node):
        """
        Includes the given node as a child node.
        """
        assert isinstance(node, Node), 'Only Node instances can be added, not %s.' % (
            type(node).__name__,)
        assert node.duration is not None, 'Duration must be specified.'
        if node in self.nodes:
            return
        #self.nodes.add(node)
        self.nodes.append(node)
        self.name_to_node[node.name] = node
        node.parent = self
        self.forward_pending.add(node)
        self._critical_path = None
        return node

    def link(self, from_node, to_node=None):
        """
        Links together two child nodes in a directed graph.
        """
        #print 'from_node:',from_node
        if not isinstance(from_node, Node):
            from_node = self.name_to_node[from_node]
        #print 'from_node:',from_node
        assert isinstance(from_node, Node)
        if to_node is not None:
            if not isinstance(to_node, Node):
                # print('to_node:', to_node)
                # print('self.name_to_node:', self.name_to_node)
                to_node = self.name_to_node[to_node]
            assert isinstance(to_node, Node)
            from_node.to_nodes.add(to_node)
            to_node.incoming_nodes.add(from_node)
        else:
            self.to_nodes.add(from_node)
            from_node.incoming_nodes.add(self)
        return self

    @property
    def first_nodes(self):
        """
        Returns all child nodes that have no in-bound dependencies.
        """
        first = set(self.nodes)
        for node in self.nodes:
            first.difference_update(node.to_nodes)
        return first

    @property
    def last_nodes(self):
        """
        Returns all child nodes that have to out-bound dependencies.
        """
        return [_ for _ in self.nodes if not _.to_nodes]

    def update_forward(self):
        """
        Updates forward timing calculations for the current node.

        Assumes the earliest start value has already been set.
        """
        changed = False
#        print 'updating forward:',self.name
        if self.es is not None and self.duration is not None:
            #            print 'es:',self.es
            #            print 'dur:',self.duration
            self.ef = self.es + self.duration
            changed = True

        if changed:
            for to_node in self.to_nodes:
                if to_node == self:
                    continue
                # Earliest start of the succeeding activity is the earliest finish
                # of the preceding activity plus possible lag.
                new_es = self.ef + to_node.lag
                if to_node.es is None:
                    to_node.es = new_es
                else:
                    to_node.es = max(to_node.es, new_es)

                if self.parent:
                    self.parent.forward_pending.add(to_node)

            if self.parent:
                self.parent.backward_pending.append(self)

    def update_backward(self):
        """
        Updates backward timing calculations for the current node.
        """
#        print 'update_backward0:',self.name,self.ls,self.lf
#        print '\tto_nodes:',[_.ls for _ in self.to_nodes]
        if self.lf is None:
            if self.to_nodes:
                #print min([_.ls for _ in self.to_nodes], 1e99999)
                self.lf = min([_.ls for _ in self.to_nodes])
            else:
                self.lf = self.ef
            #assert self.lf is not None, 'No latest finish time could be found.' #TODO
        self.ls = self.lf - self.duration
        #self.ls = (self.lf or 0) - self.duration
#        print 'update_backward1:',self.name,self.ls,self.lf

    def add_exit(self):
        """
        Links all leaf nodes to a common exit node.
        """
        if self.exit_node is None:
            self.exit_node = Node('EXIT', duration=0)
            self.add(self.exit_node)
        for node in self.nodes:
            if node is self.exit_node:
                continue
            if not node.to_nodes:
                self.link(from_node=node, to_node=self.exit_node)

    def update_all(self):
        """
        Updates timing calculations for all children nodes.
        """
        assert self.is_acyclic(), 'Network must not contain any cycles.'

        for node in list(self.forward_pending.intersection(self.first_nodes)):
            node.es = self.lag + node.lag
            node.update_forward()
            self.forward_pending.remove(node)

        i = 0
        forward_priors = set()
        while self.forward_pending:
            i += 1
#            print '\rCalculating forward paths %i...' % (i,),
#            sys.stdout.flush()
            q = set(self.forward_pending)
            self.forward_pending.clear()
            while q:
                node = q.pop()
                if node in forward_priors:
                    continue
                #forward_priors.add(node)
                node.update_forward()
#        print

        i = 0
        backward_priors = set()
        while self.backward_pending:
            i += 1
#            print '\rCalculating backward paths %i...' % (i,),
#            sys.stdout.flush()
            node = self.backward_pending.pop()
            if node in backward_priors:
                continue
            #backward_priors.add(node)
            node.update_backward()
#        print

        self._critical_path = duration, path, priors = self.get_critical_path(
            as_item=True)
        self.duration = duration
        self.es = path[0].es
        self.ls = path[0].ls
        self.ef = path[-1].ef
        self.lf = path[-1].lf

    def get_critical_path(self, as_item=False):
        """
        Finds the longest path in among the child nodes.
        """
        if self._critical_path is not None:
            # Returned cached path.
            return self._critical_path[1]
        longest = None
        q = [(_.duration, [_], set([_])) for _ in self.first_nodes]
        while q:
            item = length, path, priors = q.pop(0)
            if longest is None:
                longest = item
            else:
                try:
                    longest = max(longest, item)
                except TypeError:
                    longest = longest
            for to_node in path[-1].to_nodes:
                if to_node in priors:
                    continue
                q.append((length+to_node.duration, path
                         + [to_node], priors.union([to_node])))
        if longest is None:
            return
        elif as_item:
            return longest
        else:
            return longest[1]

    def print_times(self):
        w = 7
        print("""
+{border}+
|{blank} DUR={dur} {blank}|
+{border}+
|ES={es}|{blank}|EF={ef}|
|{segment}|{name}|{segment}|
|LS={ls}|{blank}|LF={lf}|
+{border}+
|{blank}DRAG={drag}{blank}|
+{border}+
""".format(
            blank=' '*w,
            segment='-'*w,
            border='-'*(w*3 + 2),
            dur=str(self.duration).ljust(w-4),
            es=str(self.es).ljust(w-3),
            ef=str(self.ef).ljust(w-3),
            name=str(self.name).center(w),
            ls=str(self.ls).ljust(w-3),
            lf=str(self.lf).ljust(w-3),
            drag=str(self.drag).ljust(w-5),
        ))

    # def is_acyclic1(self):
        # """
        # Returns true if the network has no cycle anywhere within it
        # by performing a depth-first search of all nodes.
        # Returns false otherwise.
        # A proper task network should be acyclic, having an explicit
        # "start" and "end" node with no link back from end to start.
        # """
        # q = [(_, set([_])) for _ in self.nodes]
        # i = 0
        # while q:
        # node, priors = q.pop(0)
        # # i += 1
        # # sys.stdout.write('\ri: %i' % i)
        # # sys.stdout.flush()
        # for next_node in node.to_nodes:
        # if next_node in priors:
        # print("Next node already in prior nodes:")
        # print(next_node.name)
        # print("Priors:")
        # for prior in sorted(priors, key=lambda n: n.name):
        # print(prior.name)

        # return False
        # next_priors = priors.copy()
        # next_priors.add(next_node)
        # q.append((next_node, next_priors))
        # return True

    def is_acyclic(self):
        g = dict((node.name, tuple(child.name for child in node.to_nodes))
                 for node in self.nodes)
        return not cyclic(g)


def critical_path_diagram(tasks, task_dependencies, filename=None, format='svg'):
    """
    Compute and draw the critical path between dependent tasks as the longest in duration from start to finish.

    Parameters
    ----------
    tasks : list of tuples where each contains a task name and dictionary for duration time
        A list of tuples where each one contains a task name and dictionary for its duration time (where keyword = "Duration" and value is a number).
    task_dependencies : list of tuples
        A list of tuples describing the dependency relationships between tasks. Each relationship is a tuple containing the predecessor task followed by its successor task. These must be the same named tasks in the task list input above.
    filename : string, optional
        A filename for the output not including a filename extension. The extension will specified by the format parameter.
    format : string, optional
        The file format of the graphic output. Note that bitmap formats (png, bmp, or jpeg) will not be as sharp as the default svg vector format and most particularly when magnified.

    Returns
    -------
    g : graph object view
        The rendered graph for display. It will be automatically displayed in Jupyter Notebooks or IPython consoles. With other Python editors it can be displayed in the associated console by typing the returned graph name (e.g., call the function with an assignment such as ``critical_path = critical_path_diagram(...)`` and then type ``critical_path`` in the console). If a filename is optionally provided, the rendered graph will also be saved as a file in the specified format. PyML calls the Graphviz API for this.

    """
    node_attr = {'color': 'black', 'fontsize': '11',
                 'shape': 'box'}  # 'fontname': 'arial',
    edge_attr = {'arrowsize': '.5', 'fontname': 'arial',
                 'fontsize': '11', 'color': 'black'}
    critical_path = graphviz.Digraph(
        'G', filename=filename, node_attr=node_attr, edge_attr=edge_attr, engine="dot", format='svg')
    critical_path.attr(rankdir='LR',)

    project = Node('')
    [project.add(Node(task[0], duration=task[1]["Duration"]))
     for task in tasks]
    [project.link(dependency[0], dependency[1])
     for dependency in task_dependencies]
    project.update_all()

    crit_path = [str(n) for n in project.get_critical_path()]
    critical_edges = [(n, crit_path[i+1])
                      for i, n in enumerate(crit_path[:-1])]
    non_critical_edges = list(set(task_dependencies) - set(critical_edges)) + \
        list(set(critical_edges) - set(task_dependencies))

    for task in tasks:
        critical_path.node(task[0], label=task[0]
                           + ', ' + str(task[1]['Duration']))

    for edge in non_critical_edges:
        critical_path.edge(edge[0], edge[1])

    for edge in critical_edges:
        critical_path.edge(edge[0], edge[1], color="red")

    print(
        f"The critical path is: {crit_path} for a project duration of {project.duration} days.")

    if filename != None:
        critical_path.render()
    return critical_path
    # next_priors = priors.copy()
    # next_priors.add(next_node)
    # q.append((next_node, next_priors))
    # return True


# determine fault tree node levels and assign them in dictionary
def assign_levels(events_quant_dict, event, level):
    for branch in events_quant_dict[event]['branches']:
        events_quant_dict[branch]['level'] = level + 1
        assign_levels(events_quant_dict, branch, level + 1)


def draw_fault_tree_diagram_quantitative(ft, filename=None, format='svg'):

    or_nodes = ['Or', 'or', 'OR']
    and_nodes = ['And', 'and', 'AND']
    basic_nodes = ['Basic', 'basic', 'BASIC']
    prob_string = lambda event_name, probability : f"<br/>p={events_quant_dict[event_name]['prob']:.1e}" if (probability<.001) else f"<br/>p={events_quant_dict[event_name]['prob']:.3f}".rstrip('0')

    # convert fault tree input to dictionary
    top_name, top_condition, top_branches = ft[0][0], ft[0][1], ft[0][3]
    events_quant_dict = {top_name: {'type': top_condition, 'prob': '', 'state': False , 'branches' : top_branches}} # calculate this
    events_quant_dict.update({event[0]:{'type': event[1],'prob': event[2], 'state': False, 'branches' : []} for event in ft if event[1] in basic_nodes})
    events_quant_dict.update({event[0]:{'type': event[1], 'prob': '', 'state': True, 'branches' : event[3]} for event in ft if event[1] in and_nodes}) # default True until False found
    events_quant_dict.update({event[0]:{'type': event[1], 'prob': '', 'state': False, 'branches' : event[3]} for event in ft if event[1] in or_nodes}) # default False until True found

    root_event = list(events_quant_dict.keys())[0]
    events_quant_dict[root_event]['level'] = 1
    assign_levels(events_quant_dict, root_event, 1)

    # compute probabilities and states
    max_level = max([events_quant_dict[event]['level'] for event in events_quant_dict])
    for level in range(max_level, 0, -1):
        for event in events_quant_dict:
            if events_quant_dict[event]['level'] == level:
                # ands
                 if events_quant_dict[event]['type'] in and_nodes:
                     probability = 1
                     events_quant_dict[event]['state'] = True  # default True until False found
                     for basic_event in events_quant_dict[event]['branches']: # the branches
                         if events_quant_dict[basic_event]['state'] is False:
                             events_quant_dict[event]['state'] = False
                         probability *= events_quant_dict[basic_event]['prob']
                     events_quant_dict[event]['prob'] = probability
                # ors
                 if events_quant_dict[event]['type'] in or_nodes:
                     probability = 0
                     events_quant_dict[event]['state'] = False  # default False until True found
                     for basic_event in events_quant_dict[event]['branches']: # the branches
                         if events_quant_dict[basic_event]['state'] is True:
                             events_quant_dict[event]['state'] = True
                         probability += events_quant_dict[basic_event]['prob']
                     events_quant_dict[event]['prob'] = probability

    # make labels with probabilities by renaming nodes
    events_quant_dict_labeled = {event+prob_string(event, events_quant_dict[event]['prob']): {'type': events_quant_dict[event]['type'], 'prob': events_quant_dict[event]['prob'], 'state': events_quant_dict[event]['state'], 'branches': events_quant_dict[event]['branches']} for event in events_quant_dict}

    for event in events_quant_dict:
        for index, branch in enumerate(events_quant_dict[event]['branches']):
            branch_label = branch+prob_string(branch, events_quant_dict[branch]['prob'])
            events_quant_dict_labeled[event+prob_string(event, events_quant_dict[event]['prob'])]['branches'][index] = branch_label

    simple_ft_quantititive = [(event, events_quant_dict_labeled[event]['type'], events_quant_dict_labeled[event]['branches']) for event in events_quant_dict_labeled]

    return(fault_tree_diagram(simple_ft_quantititive, filename=filename, format=format))

def fault_tree_cutsets(fault_tree):
    """ Returns a fault tree cutset.

    Parameters
    ----------
    ft : list of tuples
        A list of the faults as a tree hierarchy. Each fault is defined in a tuple containing the fault name, type, and underlying faults (if any) in the form
        ``("fault name", "fault name", list of fault branches)``
        with the branches as a list in the form
        ``["branch 1 name", "branch 2 name", ... "branch n name"]``
        to identify the adjoining faults. All basic events will have a blank list
        ``[]`` since they are the bottom leaves in the tree.

        The top event must be in the first row, but all other events can be in any order. They may begrouped by their event paths or by hierarchical levels as convenient. Event types can be conditional "and"s, conditional "or"s, or basic events (leaves). The following spellings are recognized as valid designations for event types:

        And: "And" "and" "AND" \n
        Or: "Or" "or" "OR" \n
        Basic: "Basic" "basic" "BASIC"

    filename : string, optional
        A filename for the output not including a filename extension. The extension will specified by the format parameter.
    format : string, optional
        The file format of the graphic output. Note that bitmap formats (png, bmp, or jpeg) will not be as sharp as the default svg vector format and most particularly when magnified.

    Returns
    -------
    cutsets : list of lists
        Returns a list of cutsets, where each is defined as a list of events.

    """
    cutsets = mocus(fault_tree)
    print("Minimal Cutsets:\nNumber  Event List")
    for num, cutset in enumerate(cutsets):
        print(num+1,'  ', cutset)

import os
import itertools
import csv

verbose = False

class ErrorMsg(Exception):
    pass

class ErrorMsg(Exception):
    """
    Taken from https://community.esri.com/thread/140022
    """
    pass

def get_ft(name):
    ft = []
    with open(name, newline='') as file:
        reader = csv.reader(file)
        ftt = list(map(tuple, reader))
    for i in ftt:
        if (i[1] == 'And' or i[1] == 'Or'):
            ft.append((i[0], i[1], i[2].split()))
        else:
            raise ErrorMsg(
                "Exception: Only And/OR gates are accepted in the Fault Tree")
    return(ft)


And = "And"
Or = "Or"


def rewrite_and(e, r, l):
    r.remove(e)
    for i in l:
        r.append(i)
    r.reverse()


def rewrite_or(e, r, l):
    new_rows = []
    x = r
    x.remove(e)
    for i in l:
        new_rows = new_rows + [([i] + x)]
    return (new_rows)

def top_to_init_path(te):
    path = []
    if te[0] == And or te[0] == "and" or te[0] == "AND":
        path = path + [te[1]]
    else:
        for x in te[1]:
            path = path + [[x]]
    return(path)


def cs_helper(i, j, p, dic_ft):
    updated_paths = p
    e = p[i][j]
    row = p[i]
    gate, inputs = dic_ft[e]
    if gate == And or gate == "and" or gate == "AND":
        rewrite_and(e, row, inputs)

    else:
        updated_paths.remove(p[i])
        new_rows = rewrite_or(e, row, inputs)
        updated_paths = updated_paths + new_rows
    return(updated_paths)


def find_element_to_expand(paths, d):
    for row in paths:
        for e in row:
            try:
                x = d[e]  # Optional -- we can return x as well
                if verbose:  print(f'{x=} {row=} {e=}') # rm
                return (paths.index(row), row.index(e))
            except KeyError:
                continue


def mocus_init(ft):
    global copy
    copy = ft
    ft  = [event for event in ft if event[1] != 'basic' if event[1] != 'Basic' if event[1] != 'BASIC']
    top_name = ft[0][0]
    dic_ft = dict([(k, [v, w]) for k, v, w in ft])
    top = dic_ft[top_name]
    ps = top_to_init_path(top)
    if verbose: print(f'{dic_ft=}') # rm
    if verbose: print(f'{ps=}') # rm

    while True:
        try:
            i, j = find_element_to_expand(ps, dic_ft)
            # print(f'{i=} {j=}') # rm
            ps = cs_helper(i, j, ps, dic_ft)
            #print(f'{ps=}') # rm
        except BaseException:
            break
    return(ps)

def mocus(fault_tree):

    verbose = False
    fault_tree_copy = deepcopy(fault_tree) # to avoid top row "and" rewrite in cs_helper
    cs = []
    cs = mocus_init(fault_tree_copy)
    css = list(map(lambda x: list(set(x)), cs))
    css.sort(key=len)
    for a, b in itertools.combinations(css, 2):
        if verbose: print(set(a), set(b)) # rm
        if set(a) <= set(b):
            try:
                css.remove(b)
            except BaseException:
                continue
    if verbose: print(f'***{css=}') # rm
    ft = copy
    return(css)
