import requests
import subprocess

# Defining few simple methods to improve the program readability
#  Function to add space
def space():
    return " "

# Function to add a new line
def newline():
    return "\n"

# Function to add a tab
def tab():
    return "\t"

class PDDLInterface:

    COLOURS = ['red', 'blue', 'orange', 'black', 'green']
    DATA_KEYS = ['actors', 'tasks', 'nodes', 'mines']
    ACTIONS = ['move', 'mine', 'pick-up', 'drop', 'start-building', 'deposit', 'complete-building']

    @staticmethod
    # Function to write a temporal problem file
    def writeProblem(world_info, problem_file_path="agents/problem-temporal.pddl"):
        actors = world_info['actors'].values()
        tasks = world_info['tasks'].values()

        with open(problem_file_path, "w") as file:

            file.write("(define(problem craft-bots-temporal-prob)" + newline())
            file.write(newline())
            file.write("(:domain craft-bots-temporal)" + newline())
            file.write(newline())

        ###################################################### OBJECTS ######################################################

            file.write("(:objects" + newline())

            file.write(tab() + ";; Declaring the objects for the problem" + newline())
            for world_info_data_key in PDDLInterface.DATA_KEYS:
                file.write(tab())
                for actor in world_info[world_info_data_key].values():
                    file.write(f"{world_info_data_key[0]}{str(actor['id'])} ")
                file.write(f"- {world_info_data_key[:-1]}" + newline())

            file.write(tab())
            for i in PDDLInterface.COLOURS:
                file.write(str(i) + space())
            file.write(f"- color" + newline())

            file.write(")")
            file.write(newline() * 2)

        ######################################################## INIT ########################################################

            file.write("(:init" + newline())

            file.write(tab() + ";; setting the initial node for each actor" + newline())
            for actor in actors:
                actor_id = str(actor['id'])
                actor_node = str(actor['node'])

                # Actor's location
                file.write(tab())
                file.write(f"(actor_location a{actor_id} n{actor_node})")
                file.write(newline())

                file.write(tab())
                file.write(f"(= (move_speed a{str(actor['id'])}) 5)")
                file.write(newline())

                # Number of resources present in Actor's inventory, which is initialy 0
                file.write(tab())
                file.write(f"(= (total_resource_in_inventory a{str(actor['id'])}) 0)")
                file.write(newline())
                file.write(newline())

            file.write(newline())
            file.write(tab() + ";; setting the connection between each nodes" + newline())
            for edge in world_info['edges'].values():
                node_A = str(edge['node_a'])
                node_B = str(edge['node_b'])
                edge_length = str(edge['length'])

                file.write(tab() + f"(connected n{node_A} n{node_B})")
                file.write(tab() + f"(connected n{node_B} n{node_A})")
                file.write(newline())

                file.write(tab() + f"(= (edge_length n{node_A} n{node_B}) {edge_length})")
                file.write(tab() + f"(= (edge_length n{node_B} n{node_A}) {edge_length})")
                file.write(newline())
            file.write(newline())

            file.write(tab() + ";; setting the mines details" + newline())
            for mine in world_info['mines'].values():
                mine_id = str(mine['id'])
                mine_node = str(mine['node'])
                mine_color = PDDLInterface.COLOURS[mine['colour']]
                file.write(tab() + f"(mine_detail m{mine_id} n{mine_node} {mine_color})" + newline())
            file.write(newline())
                        
            for task in tasks:
                task_id = str(task['id'])
                task_node = str(task['node'])
                is_task_completed = task['completed']

                if not is_task_completed:
                    file.write(tab() + f"(site_not_created t{task_id} n{str(task['node'])})" + newline())
                    file.write(tab() + f"(building_not_built t{task_id} n{task_node})" + newline())
                    file.write(newline())

            file.write(newline())

            file.write(newline())
            file.write(tab() + ";; set function to count the number of resources carried by the actor" + newline())
            for actor in actors:  
                actor_id = str(actor['id'])
                for color in PDDLInterface.COLOURS:
                    file.write(tab())
                    file.write(f"(= (count_of_resource_carried a{actor_id} {color}) 0)")
                    file.write(newline())
                file.write(newline())
                        
            file.write(tab() + ";; set function to count total and individual resources required for a task" + newline())
            for task in tasks:
                task_id = str(task['id'])
                task_node = str(task['node'])
                resource_list = task['needed_resources']
                is_task_completed = task['completed']

                if not is_task_completed:
                    file.write(tab())
                    file.write(f"(= (total_resource_required t{task_id} n{task_node}) {str(sum(resource_list))})")
                    file.write(newline())

                    for index, color in enumerate(PDDLInterface.COLOURS):
                        resource_needed = resource_list[index]

                        if resource_needed>0:
                            file.write(tab())
                            file.write(f"(= (individual_resource_required t{task_id} {color}) {str(resource_needed)})")
                            file.write(newline())
                file.write(newline())

            for actor in actors:
                for actor2 in actors:
                    if actor['id'] != actor2['id']:
                        file.write(tab() + f"(not-same a{str(actor['id'])} a{str(actor2['id'])})")
                        file.write(tab() + f"(not-same a{str(actor2['id'])} a{str(actor['id'])})" + newline())
            file.write(newline())

            # blue resource takes twice as long to mine
            blue_resource = PDDLInterface.COLOURS.index('blue')
            orange_resource = PDDLInterface.COLOURS.index('orange')
            for mine in world_info['mines'].values():
                color_id = mine['colour']
                if color_id == blue_resource:
                    file.write(tab())
                    file.write(f"(= (mine_duration_blue m{str(mine['id'])}) {str(33 * 2)})" + newline())
                else:
                    file.write(tab())
                    file.write(f"(= (mine_duration m{str(mine['id'])}) {str(33)})" + newline())
            file.write(newline())

            for colour1 in PDDLInterface.COLOURS:
                for colour2 in PDDLInterface.COLOURS:
                    prefix = "is_" if colour1 == colour2 else "not_"
                    file.write(tab() + f"({prefix}{colour2} {colour1})" + newline())
                file.write(newline())
            file.write(newline())

            for i in range(0, 20000, 1200):
                file.write(tab())
                file.write(f"(at {str(i)} (red_available red))" + newline())

            file.write(')')
            file.write(newline())

        ######################################################## GOAL ########################################################

            file.write("(:goal" + newline())
            file.write(tab() + '(and' + newline())

            # fetch the tasks from the world info
            for task in tasks:
                task_id = str(task['id'])
                task_node = str(task['node'])
                is_task_completed = task['completed']

                if not is_task_completed:
                    file.write(tab() * 2)
                    file.write(f"(building_built t{task_id} n{task_node})" + newline())

            file.write(")))" + newline())
            file.close()

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
        # data = {'domain': open(domain, 'r').read(), 'problem': open(problem, 'r').read()}
        # resp = requests.post('https://popf-cloud-solver.herokuapp.com/solve', verify=True, json=data).json()
        # if not 'plan' in resp['result']:
        #     if verbose:
        #         print("WARN: Plan was not found!")
        #         print(resp)
        #     return False
        # with open(plan, 'w') as f:
        #     f.write(''.join([act for act in resp['result']['plan']]))
        # f.close()

        optic_path = '/home/mlb23172/bin/optic-cplex'
        response = str(subprocess.run([f'{optic_path}', '-N', f'{domain}', f'{problem}'], stdout=subprocess.PIPE))
        start_index = response.rindex('Solution Found')

        if start_index == -1:
            return False

        trimmed_plan = response[start_index:-2]
        trimmed_response_list = trimmed_plan.split('\\n')[4:]
        transformed_string = '\n'.join(list(filter(lambda x: x != "", trimmed_response_list)))

        with open(plan, "w") as file:
            file.write(transformed_string)

        return True

if __name__ == '__main__':
    PDDLInterface.generatePlan("agents/domain-craft-bots-temporal.pddl", "agents/problem-temporal.pddl", "agents/plan-temporal.pddl", verbose=True)
    plan = PDDLInterface.readPDDLPlan('agents/plan-temporal.pddl')
    print(plan)