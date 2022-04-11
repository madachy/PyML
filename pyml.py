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
