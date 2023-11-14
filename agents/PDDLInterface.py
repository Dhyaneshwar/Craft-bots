from collections.abc import Set
from typing import List, Tuple, Union
import requests
import json 
from agents.space_handler import SpaceHandler

class PDDLInterface:

    COLOURS = ['red', 'blue', 'orange', 'black', 'green']
    DATA_KEYS = ['actors', 'tasks', 'nodes', 'mines']
    ACTIONS = ['move', 'mine', 'pick-up', 'drop', 'start-building', 'deposit', 'complete-building']

    @staticmethod
    # Function to write a problem file
    # Complete this function

    def writeProblem(world_info, file="pddl/problem.pddl"):
        # Function that will write the problem file
        # write a simple config that will create 10 randomly generated nodes, and 6 fixed tasks (again, randomly generated).
        # Each task will require a different number of resources to solve

        spaceHandler = SpaceHandler()
        with open(file, "w") as file:

            file.write("(define(problem craft-bots-prob)")
            file.write(spaceHandler.newline * 2)
            file.write("(:domain craft-bots)")
            file.write(spaceHandler.newline * 2)

        ###################################################### OBJECTS ######################################################

            file.write("(:objects" + spaceHandler.newline)

            for world_info_data_key in PDDLInterface.DATA_KEYS:
                file.write(spaceHandler.tab)
                for actor in world_info[world_info_data_key].values():
                    file.write(f"{world_info_data_key[0]}{str(actor['id'])} ")
                file.write(f"- {world_info_data_key[:-1]}" + spaceHandler.newline)

            file.write(spaceHandler.tab)
            for i in PDDLInterface.COLOURS:
                file.write(str(i) + spaceHandler.space)
            file.write(f"- color" + spaceHandler.newline)

            file.write(spaceHandler.close_paren)
            file.write(spaceHandler.newline * 2)

        ######################################################## INIT ########################################################

            file.write("(:init" + spaceHandler.newline)

            # setting the initial node for each actor
            for actor in world_info['actors'].values():
                actor_id = actor['id']
                actor_node = actor['node']
                file.write(spaceHandler.tab)
                file.write(f"(alocation a{str(actor_id)} n{str(actor_node)})")
                file.write(spaceHandler.newline)

            # setting the connection between each nodes
            file.write(spaceHandler.newline)
            for edge in world_info['edges'].values():
                node_A = str(edge['node_a'])
                node_B = str(edge['node_b'])
                file.write(spaceHandler.tab)
                file.write(f"(connected n{node_A} n{node_B})")
                file.write(spaceHandler.tab)
                file.write(f"(connected n{node_B} n{node_A})")
                file.write(spaceHandler.newline)

            # setting the initial mines location
            file.write(spaceHandler.newline)
            for mine in world_info['mines'].values():
                mine_id = str(mine['id'])
                mine_node = str(mine['node'])
                mine_color = PDDLInterface.COLOURS[mine['colour']]
                file.write(spaceHandler.tab)
                file.write(f"(mine_detail m{mine_id} n{mine_node} {mine_color})" + spaceHandler.newline)

            # set the variables not_created_site, not_carrying, not_deposited
            file.write(spaceHandler.newline)
            for task in world_info['tasks'].values():
                if not world_info['tasks'][task['id']]['completed']:
                    for actor in world_info['actors'].values():  
                        actor_id = str(actor['id'])
                        task_node = str(task['node'])
                        for color in PDDLInterface.COLOURS:
                            file.write(spaceHandler.tab)
                            file.write(f"(not_carrying a{actor_id} {color})" + spaceHandler.newline)
                            file.write(spaceHandler.tab)
                            file.write(f"(not_deposited a{actor_id} {color} n{task_node})" + spaceHandler.newline)
                        file.write(spaceHandler.newline)
                    break
                        
            for task in world_info['tasks'].values():
                if not world_info['tasks'][task['id']]['completed']:
                    file.write(spaceHandler.tab)
                    file.write(f"(not_created_site n{str(task['node'])})" + spaceHandler.newline)
                    break

            for task in world_info['tasks'].values():
                if not world_info['tasks'][task['id']]['completed']:
                    for index, color in enumerate(PDDLInterface.COLOURS):
                        num_needed = task['needed_resources'][index]
                        if num_needed > 0:
                            file.write(spaceHandler.tab)
                            file.write('(= (color_count' + spaceHandler.space + str(color) + spaceHandler.space + 'n' + str(task['node']) + ')' + spaceHandler.space + str(num_needed) + ')' + spaceHandler.newline)
                    break

            file.write(spaceHandler.close_paren)
            file.write(spaceHandler.newline * 2)

        ######################################################## GOAL ########################################################

            file.write("(:goal" + spaceHandler.newline)
            file.write(spaceHandler.tab + '(and' + spaceHandler.newline)

            # fetch the tasks from the world info
            for task in world_info['tasks'].values():
                if not world_info['tasks'][task['id']]['completed']:
                    for index, color in enumerate(PDDLInterface.COLOURS):
                        num_needed = task['needed_resources'][index]
                        if num_needed > 0:
                            file.write(spaceHandler.tab * 2)
                            file.write('(= (color_count' + spaceHandler.space + str(color) + spaceHandler.space + 'n' + str(task['node']) + ')' + spaceHandler.space + str(0) + ')' + spaceHandler.newline)
                            # break
                        # break
                    break

            file.write(")))" + spaceHandler.newline)

    @staticmethod
    # Completed already, will read a generated plan from file
    def readPDDLPlan(file: str):
        plan = []
        with open(file, "r") as f:
            line = f.readline().strip()
            while line:
                tokens = line.split()
                action = tokens[1][1:]
                params = tokens [2:-1]
                # remove trailing bracket
                params[-1] = params[-1][:-1]
                # remove character prefix and convert colours to ID
                params = [int(p[1:]) if p not in PDDLInterface.COLOURS else PDDLInterface.COLOURS.index(p) for p in params]
                plan.append((action, params))
                line = f.readline().strip()
            f.close()
        return plan

    @staticmethod
    # Completed already
    def generatePlan(domain: str, problem: str, plan: str, verbose=False):
        data = {'domain': open(domain, 'r').read(), 'problem': open(problem, 'r').read()}
        resp = requests.post('https://popf-cloud-solver.herokuapp.com/solve', verify=True, json=data).json()
        if not 'plan' in resp['result']:
            if verbose:
                print("WARN: Plan was not found!")
                print(resp)
            return False
        with open(plan, 'w') as f:
            f.write(''.join([act for act in resp['result']['plan']]))
        f.close()
        return True

if __name__ == '__main__':
    PDDLInterface.generatePlan("pddl/domain-craft-bots.pddl", "pddl/problem.pddl", "pddl/plan.pddl", verbose=True)
    plan = PDDLInterface.readPDDLPlan('pddl/plan.pddl')
    print(plan)