import numpy as np
import pandas as pd
import math
import random
import itertools
import sys
import matplotlib.pyplot as plt


from environment import restocking_game
from agent import agent

CUSTOMERS = {1: {'Position': (4, 1), 'Capacity': 1000, 'Level': 1000},
             2: {'Position': (0, 3), 'Capacity': 750, 'Level': 750},
             3: {'Position': (3, 4), 'Capacity': 500, 'Level': 500}}

CUSTOMER_LOCATIONS = {(4, 1): 1, (0, 3): 2, (3, 4): 3, (2, 2): -1}


CUSTOMERS_TRUCK = {1: {'Position': (4, 1), 'Capacity': 1000, 'Level': 1000},
             2: {'Position': (0, 3), 'Capacity': 750, 'Level': 750},
             3: {'Position': (3, 4), 'Capacity': 500, 'Level': 500},
             -1: {'Position': "NA", 'Capacity': 1000, 'Level': 1000}}

TRUCK = {'Position': (4, 1), 'Capacity': 2000, 'Level': 2000}

ACTIONS = {'U': ((-1, 0), 0), 'D': ((1, 0), 1), 'L': ((0, -1), 2), 'R': ((0, 1), 3), 'I': ((0, 0), 4) }

def level_category(level, capacity):
    level_class = round(round(level / capacity, 1) * 5)
    return level_class

def return_action(index):
    action = ""
    if index == 0:
        action = 'U'
    elif index == 1:
        action = 'D'
    elif index == 2:
        action = 'L'
    elif index == 3:
        action = 'R'
    elif index == 4:
        action = 'I'
    else:
        action == "ERROR"
    return action

map_size = (5,5)
level_combinations = []
level_combinations = list(list(zip(CUSTOMERS_TRUCK, element))
           for element in itertools.product(range(0,6), repeat = len(CUSTOMERS_TRUCK)))
game_states = []
for i in range(map_size[0]):
    for j in range(map_size[1]):
        position = (i, j)
        for combination in level_combinations:
            state = str(position) + " | " + str(combination)
            game_states.append(state)


if __name__ == '__main__':
            
    simulations = sys.argv[1]   

    game = restocking_game(CUSTOMERS, CUSTOMER_LOCATIONS, TRUCK, 5, 5)
    player = agent(game.reward_table, game_states, alpha = 0.3, gamma = 0.2, random_factor = 0.3, customer_input = CUSTOMERS, truck_input = TRUCK, map_length = 5, map_width = 5)
    i = 1

    simulation_file = simulations + "_simulations.txt"
    q_file = simulations + "_q_table.txt"
    f = open(simulation_file, "a")
    epochs = []

    while (i <= 0): #int(simulations)):
        ## SIMULATE EACH GAME UNTIL GAME OVER (ALL TANKS EMPTY)
        game.reset()
        move_history = []
        game.customers[1]['Level'] = 300

        j = 1
        while not game.is_game_over():
            state = game.return_state()
            
            f.write("\nSimulation {} epoch {}\n".format(i, j))
            f.write("State: {}\n".format(state))
            possible_new_states = {}
            for action in game.allowed_states[state]:
                possible_new_states[action] = game.next_state(state, action)
            next_move = player.learn(state, game.allowed_states[state], game.reward_table, possible_new_states, f)
            game.take_action(next_move)
            if j % 5 == 0 and j != 0:
                game.update_levels()
                #print("Levels have been updated")
            j += 1
        #print("Simulation {} had {} epochs".format(i, j))
        #statement = "Simulation " + str(i) + " had " + str(j) + " epochs.\n"
        #f.write(statement)
        i += 1
        epochs.append(j)
        player.update()
        #print(player.random_factor)
    f.close()
    f = open(q_file, "a")



    for state, values in player.Q.items():
        #print(state, values)    
        statement = str(state) + str(values) + str("\n")
        f.write(statement)
    f.close()



    graph_file = simulations + "_graph.png"

    simulations_x = np.array(range(1, int(simulations) + 1))
    epochs_y = np.array(epochs)


    fig, ax = plt.subplots(1,1)
    ax.plot(simulations_x, epochs_y)
    fig.savefig(graph_file)
    #print(simulations_x)
    #print(epochs_y)


            


