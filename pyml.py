import graphviz
import textwrap
import os

def context_diagram(system, external_systems, filename=None, format='svg', engine='dot'):
    node_attr={'color': 'black', 'fontsize': '11',  'shape':'box'} # 'fontname': 'arial', 
    c = graphviz.Graph('G', node_attr=node_attr, filename=filename, format=format, engine=engine)
    for external_system in external_systems:
        c.edge(system, external_system)
    if filename != None: 
        c.render() # render and save file, clean up temporary dot source file (no extension) after successful rendering with (cleanup=True) doesn't work on windows "permission denied"
    return c

def activity_diagram(element_dependencies, filename=None, format='svg'):
    node_attr={'color': 'black', 'fontsize': '11',  'style': "rounded", 'shape':'box'} # 'fontname': 'arial',
    edge_attr={'arrowsize': '.5', 'fontname': 'arial', 'fontsize': '11', }
    activity = graphviz.Digraph('G', filename=filename, node_attr=node_attr, edge_attr=edge_attr, engine="dot", format='svg')
    activity.attr(rankdir='LR',)
    activity.edges(element_dependencies)

    if filename != None: 
        activity.render() # render and save file, clean up temporary dot source file (no extension) after successful rendering with (cleanup=True) doesn't work on windows "permission denied"
        #os.remove(filename) also doesn't work on windows "permission denied"
    return activity

def use_case_diagram(system_name, actors, use_cases, interactions, use_case_relationships, filename):
    node_attr={'color': 'black', 'fontname': 'arial', 'fontsize': '11',  'width':'0.'}
    edge_attr={'arrowsize': '.5', 'fontname': 'arial', 'fontsize': '11', }
    u = graphviz.Digraph('G', filename=filename, node_attr=node_attr, edge_attr=edge_attr, engine="neato", format='svg')
    system_height = len(use_cases) + .5

    u.node(system_name, label=f'''<<b>{system_name}</b>>''', pos=f'0,{(system_height+.5)/2}!', shape="box", height=f"{system_height}", width="2", labelloc="t")
    
    column=-2
    for number, actor in enumerate(actors):
        division = system_height / (len(actors) + 1)
        #print (division)
        u.node(actor, pos=f'{column}, {system_height - division*(number+1) + .25}!', width='.1', shape='none', image='actor.svg', labelloc='b')
    
    column=0
    for number, use_case in enumerate(use_cases):
        u.node(use_case, pos=f'{column}, {len(use_cases)-number}!', width='1.25', height=".7")
    
    for edge in (interactions):
        u.edge(edge[0], edge[1]) # lhead='clusterx' not used
       
    if filename != None: 
        u.render() # render and save file, clean up temporary dot source file (no extension) after successful rendering with (cleanup=True) doesn't work on windows "permission denied"
        #os.remove(filename) also doesn't work on windows "permission denied"
    return u

def sequence_diagram(system_name, actors, objects, actions, filename):
    verbose = False
    wrap_width = 40
    wrap = lambda text : textwrap.fill(text, width=wrap_width, break_long_words=False)
    graph_attr={'rankdir':'LR', 'color': 'black'} 
    node_attr={'shape': 'point', 'color': 'none', 'fontname': 'arial', 'fontsize': '11',  'width':'0.'}
    edge_attr={'arrowsize': '.5', 'fontname': 'arial', 'fontsize': '11', }
    g = graphviz.Digraph('G', filename=filename, graph_attr=graph_attr, node_attr=node_attr, edge_attr=edge_attr, engine="neato", format='svg')
    
    # spread actors/objects apart on x-axis, differentiate actors from objects for images used
    object_spacing = 3
    object_x_coords = {} # dictionary holds x coordinates for action nodes and edges
    for actor_object_number, actor_object in enumerate(actors+objects, start=1):
        x = int(actor_object_number-1)*object_spacing
        if actor_object in actors: g.node(actor_object, pos=f"{x},.2!", shape="none", image='actor.svg', labelloc='b') 
        if actor_object in objects: g.node(actor_object, pos=f"{x},.2!", shape="box", color='black') 
        object_x_coords[actor_object] = x
    
    # create nodes for each action source and destination to draw arrows to/from
    # must capture last action # to draw lifelines to
    object_last_actions = {} # dictionary holds last action for objects and actors
        
    for action_number, action in enumerate(actions, start=1):
        for actor_object, x in object_x_coords.items():
            y = int(action_number)*.4
            if action[0] == actor_object: g.node(f'{action[0]} {int(action_number)}', pos=f"{x},-{y}!") # arrow node names: actor/object  action #
            if action[1] == actor_object: g.node(f'{action[1]} {int(action_number)}', pos=f"{x},-{y}!")
            if actor_object == action[0] or actor_object == action[1]: object_last_actions[actor_object] = action_number 
            if verbose: print(actor_object, f'{action[0]}->{action[1]} # {int(action_number)}', f"pos {x},-{y}!")
     
    # edges for each arrow going down
    for action_number, action in enumerate(actions, start=1):
        source_x, target_x = object_x_coords[action[0]], object_x_coords[action[1]]
        g.edge(f'{action[0]} {int(action_number)}', f'{action[1]} {int(action_number)}',  headlabel=f'{wrap(action[2]) if len(action[2]) > wrap_width else action[2]}', labeldistance=str(object_spacing * 3.6), labelangle=f'{-5 if source_x < target_x else 5}') # left to right -10 with x separation = 1 wrap = 25 .5 y,  right to left 15 with x separation = 1 wrap = 25 .5y
            
    # lifelines
    for actor_object in actors+objects:
        if verbose: print(actor_object, f'{actor_object} {len(actions)}')
        g.edge(actor_object, f'{actor_object} {object_last_actions[actor_object]}', style='dashed', arrowhead='none') #
        
    if verbose: print(object_x_coords)
    if verbose: print(object_last_actions)
    if filename != None: 
        g.render() # render and save file, clean up temporary dot source file (no extension) after successful rendering with (cleanup=True) doesn't work on windows "permission denied"
        #os.remove(filename) also doesn't work on windows "permission denied"
    return g 
    
def design_structure_matrix(elements, element_dependencies, filename=None, format='svg'):
    cell_width = 20 # pixels
    
    dependency_elements = [dependency[0:2] for dependency in element_dependencies]
    
    node_string = '<table border="0" cellborder="1"  cellspacing="0">'
    for row, element  in enumerate((['']+elements)):
        node_string += '<tr>'
        if row == 0:
            for column, element in enumerate((['']+elements)):
                node_string += f'<td height="{cell_width}px" width="{cell_width}px">' + element + '</td>'
        else:
            for column, element in enumerate((['']+elements)):
                if column > 0:
                    if row == column:
                        node_string += '<td bgcolor="black"></td>'
                    else:
                        cell_dependency_tuple = (elements[column-1], elements[row-1]) # e.g. ('B', 'A')
                        if cell_dependency_tuple in dependency_elements:
                            if len(element_dependencies[dependency_elements.index(cell_dependency_tuple)]) == 2: 
                                node_string += f'<td height="{cell_width}px" width="{cell_width}px">' + 'X' + '</td>' # default 'X' label
                            if len(element_dependencies[dependency_elements.index(cell_dependency_tuple)])!= 2: 
                                node_string += f'<td height="{cell_width}px" width="{cell_width}px">' + element_dependencies[dependency_elements.index(cell_dependency_tuple)][2] + '</td>' # custom label
                            # print('<td height="{cell_width}px" width="{cell_width}px">', row, column, '</td>')
                        else:
                            node_string += f'<td height="{cell_width}px" width="{cell_width}px">' + '' + '</td>'
                else:
                    node_string += f'<td height="{cell_width}px" width="{cell_width}px">' + elements[row-1] + '</td>'
        node_string += '</tr>'
    node_string += '</table>'
    
    dsm = graphviz.Digraph('dsm', filename=filename, format=format, node_attr={'shape': 'plaintext'})
    dsm.node('dsm', f'''<{node_string}>''')
    #dsm.view()
    if filename != None: 
        dsm.render() # render and save file, clean up temporary dot source file (no extension) after successful rendering with (cleanup=True) doesn't work on windows "permission denied"
        #os.remove(filename) also doesn't work on windows "permission denied"
    return dsm