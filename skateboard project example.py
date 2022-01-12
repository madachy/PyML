import pyml

system = 'Skateboard'
external_systems = ['Skateboarder']
pyml.context_diagram(system, external_systems, filename="skateboard_context_diagram")

use_cases = ['Ride Board']
actors = ['Skateboarder']
interactions = [('Skateboarder', 'Ride Board')]
pyml.use_case_diagram(system, actors, use_cases, interactions, use_case_relationships=[], filename="skateboard_use_case_diagram")

task_dependencies = [('Make Board', 'Assemble'), ('Acquire Wheels', 'Assemble')]
pyml.activity_diagram(task_dependencies, filename="skateboard_activity_diagram")
    
tasks = ['Make Board', 'Acquire Wheels', 'Assemble']
pyml.design_structure_matrix(tasks, task_dependencies, filename="skateboard_task_dsm")

parameters = ['Requirements', 'Board Size', 'Wheel Diameter', 'Cost']
parameter_dependencies = [('Requirements', 'Board Size'), ('Requirements', 'Wheel Diameter'), ('Board Size', 'Cost'), ('Wheel Diameter', 'Cost')]
pyml.design_structure_matrix(parameters, parameter_dependencies, filename="skateboard_parameter_dsm")

"""
Task Feedback
"""
task_dependencies = [('Make Board', 'Assemble'), ('Acquire Wheels', 'Assemble'), ('Assemble', 'Test'), ('Test', 'Assemble')]
pyml.activity_diagram(task_dependencies, filename="skateboard_activity_diagram_with_feedback")

tasks = ['Make Board', 'Acquire Wheels', 'Assemble', 'Test']
pyml.design_structure_matrix(tasks, task_dependencies, filename="skateboard_task_dsm_with_feedback")
