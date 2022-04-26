from __future__ import print_function
import graphviz
import textwrap
import os
import sys

def context_diagram(system, external_systems, filename=None, format='svg', engine='dot'):
    node_attr = {'color': 'black', 'fontsize': '11',
                 'shape': 'box'}  # 'fontname': 'arial',
    c = graphviz.Graph('G', node_attr=node_attr,
                       filename=filename, format=format, engine=engine)
    for external_system in external_systems:
        c.edge(system, external_system)
    if filename is not None:
        c.render()  # render and save file, clean up temporary dot source file (no extension) after successful rendering with (cleanup=True) doesn't work on windows "permission denied"
    return c


def activity_diagram(element_dependencies, filename=None, format='svg'):
    node_attr = {'color': 'black', 'fontsize': '11',
                 'style': "rounded", 'shape': 'box'}  # 'fontname': 'arial',
    edge_attr = {'arrowsize': '.5', 'fontname': 'arial', 'fontsize': '11', }
    activity = graphviz.Digraph('G', filename=filename, node_attr=node_attr,
                                edge_attr=edge_attr, engine="dot", format='svg')
    activity.attr(rankdir='LR',)
    activity.edges(element_dependencies)

    if filename != None:
        activity.render()  # render and save file, clean up temporary dot source file (no extension) after successful rendering with (cleanup=True) doesn't work on windows "permission denied"
        #os.remove(filename) also doesn't work on windows "permission denied"
    return activity


def use_case_diagram(system_name, actors, use_cases, interactions, use_case_relationships, filename):
    node_attr = {'color': 'black', 'fontname': 'arial',
                 'fontsize': '11',  'width': '0.'}
    edge_attr = {'arrowsize': '.5', 'fontname': 'arial', 'fontsize': '11', }
    u = graphviz.Digraph('G', filename=filename, node_attr=node_attr,
                         edge_attr=edge_attr, engine="neato", format='svg')
    system_height = len(use_cases) + .5

    u.node(system_name, label=f'''<<b>{system_name}</b>>''', pos=f'0,{(system_height+.5)/2}!',
           shape="box", height=f"{system_height}", width="2", labelloc="t")

    column = -2
    for number, actor in enumerate(actors):
        division = system_height / (len(actors) + 1)
        #print (division)
        u.node(actor, pos=f'{column}, {system_height - division*(number+1) + .25}!',
               width='.1', shape='none', image='actor.svg', labelloc='b')

    column = 0
    for number, use_case in enumerate(use_cases):
        u.node(
            use_case, pos=f'{column}, {len(use_cases)-number}!', width='1.25', height=".7")

    for edge in (interactions):
        u.edge(edge[0], edge[1])  # lhead='clusterx' not used

    if filename != None:
        u.render()  # render and save file, clean up temporary dot source file (no extension) after successful rendering with (cleanup=True) doesn't work on windows "permission denied"
        #os.remove(filename) also doesn't work on windows "permission denied"
    return u


def sequence_diagram(system_name, actors, objects, actions, filename):
    verbose = False
    wrap_width = 40
    def wrap(text): return textwrap.fill(
        text, width=wrap_width, break_long_words=False)
    graph_attr = {'rankdir': 'LR', 'color': 'black'}
    node_attr = {'shape': 'point', 'color': 'none',
                 'fontname': 'arial', 'fontsize': '11',  'width': '0.'}
    edge_attr = {'arrowsize': '.5', 'fontname': 'arial', 'fontsize': '11', }
    g = graphviz.Digraph('G', filename=filename, graph_attr=graph_attr,
                         node_attr=node_attr, edge_attr=edge_attr, engine="neato", format='svg')

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
    verbose = False
    node_attr = {'color': 'black', 'fontsize': '11',
                 'shape': 'plaintext'}  # 'fontname': 'arial',
    edge_attr = {'arrowtail': 'none', 'arrowsize': '0', 'dir': 'both', 'penwidth': '2', 'fontname': 'arial', 'fontsize': '11', } #https://graphviz.org/docs/attr-types/arrowType/
    fault_tree = graphviz.Digraph('G', filename=filename, node_attr=node_attr,
                                edge_attr=edge_attr, engine="dot", format='svg')
    fault_tree.attr(rankdir='TB', splines='polyline',  )
    

    # create required SVG included files

    and_node = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
   width="50"
   height="45"
   id="svg2"
   version="1.0"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:dc="http://purl.org/dc/elements/1.1/">
  <defs
     id="defs4" />
  <metadata
     id="metadata7">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
      </cc:Work>
    </rdf:RDF>
  </metadata>
   <g transform="translate(-15.,0.0)"
     id="layer1">
     <path
        style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:medium;line-height:normal;font-family:'Bitstream Vera Sans';-inkscape-font-specification:'Bitstream Vera Sans';text-indent:0;text-align:start;text-decoration:none;text-decoration-line:none;letter-spacing:normal;word-spacing:normal;text-transform:none;writing-mode:lr-tb;direction:ltr;text-anchor:start;display:inline;overflow:visible;visibility:visible;
        fill:black;fill-opacity:1;
        stroke:blue;stroke-width:0;
        marker:none;enable-background:accumulate"
        d="m 5.238095,45.238095 h 1.428571 37.142858 1.428571 V 43.809524 24.761905 c 0,-11.267908 -9.000045,-20 -20,-20 -10.999955,0 -20,8.732091 -20,20 0,0 0,0 0,19.047619 z m 2.857143,-2.857143 c 0,-7.977121 0,-13.061225 0,-15.238095 0,-1.190476 0,-1.785714 0,-2.083333 0,-0.14881 0,-0.230656 0,-0.267858 0,-0.0186 0,-0.02511 0,-0.02976 0,-9.760663 7.639955,-16.666667 17.142857,-16.666667 9.502902,0 17.142857,7.382195 17.142857,17.142857 v 17.142857 z"
        id="path2884" />
  </g>
</svg>"""

    or_node = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   width="50"
   height="49"
   version="1.1"
   xmlns="http://www.w3.org/2000/svg">
   <g transform="translate(-22.95,0.3)">
  <path
     fill="none"
     stroke="#000000"
     stroke-width="3"
     d="M 48.32812,4.1093798 48.328126,0.04673552 M 48.32812,49.95376 48.32812,43.305394 48.32812,40.81263"
     id="path380" />
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
     <line x1="48.35" x2="48.35" y1="0" y2="3" stroke="black" stroke-width="3"/>
   </g>
 </svg>"""

    f3 = open("AND_node.svg", "w")    
    f3.write(and_node)
    f3.close()

    f2 = open("OR_node.svg", "w")    
    f2.write(or_node)
    f2.close()
    
    f2 = open("OR_node_bottom.svg", "w")    
    f2.write(or_node_bottom)
    f2.close()
    
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
              <tr><td port="top">{node_name}</td></tr>
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
        else:
            fault_tree.node(node_name, f'''<
            <table border="0" cellborder="0" cellspacing="0" cellpadding="0">
              <tr>
            <td > 
            <table border="0" cellborder="1" cellspacing="0" cellpadding="0">
              <tr><td port="top">{node_name}</td></tr>
            </table>
            </td>
              </tr>
              <tr>
                <td port="{node_type}"><img src="{node_type}_node.svg"/></td>  
              </tr>
              <tr>
                <td><img src="OR_node_bottom.svg"/></td> 
              </tr>
            </table>>''')
        if verbose: print("Leaves")
        for leaf in leafs:
            if verbose: print(node_name,'->', leaf)
            fault_tree.edge(node_name+':'+node_type+':s', leaf+':top:n') # leaf+':top:n' closer but not symmetrical
            
    if filename != None:
        fault_tree.render()
        
    return fault_tree  

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


def fault_tree_cutsets(fault_tree):
    print("Cutsets: ", mocus(fault_tree))
    
'''
===============================================================================
    File name: cutsets.py
    Authors: Umair Siddique, Ray Madachy
    Description: Accepts a fault tree and generates the minimal cutsets
    Licence: MIT
===============================================================================
'''
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
    cs = []
    cs = mocus_init(fault_tree)
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
