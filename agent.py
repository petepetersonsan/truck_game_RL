import numpy as np
import pandas as pd
import math
import random
import itertools
import re


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

def type_changer(variable):
    if variable[0] == "(":
        x = int(variable[1])
        y = int(variable[4])
        new = (x, y)
    else:
        temp = re.sub(r"\)\, ", ") | ", re.sub(r"[\[\]]", "", variable)).split(" | ")
        new = []
        for element in temp:
            entity, level = element.split(", ")
            entity = int(entity[1:])
            level = re.sub(r"\'", "", level[:-1])
            new.append((entity, int(level)))
    return new

class agent(object):
    def __init__(self, reward_table, states,  customer_input, truck_input, map_length, map_width, alpha = 0.15, gamma = 0.2, random_factor = 0.3):
        first_state = str((0, 0)) + " | " + str([(1, 5), (2, 5), (3, 5), (-1, 5)])
        self.state_history = []
        self.state_history.append((first_state, 0))
        self.alpha = alpha
        self.random_factor = random_factor
        self.customer_data = customer_input
        self.truck_data = truck_input
        self.map_length = map_length
        self.map_width = map_width
        
        ## The G Table is the expected reward the agent will receive for each state.
        ## Remember, the state is the position of the truck as well as the level 
        ## of the customers and the truck.
        
        self.Q = {}

        self.G = {}
        self.init_reward(reward_table)

        ### Fix for 
    def init_reward(self, reward_table):
        for state in reward_table.keys():
            #self.Q[state] = np.random.uniform(high = 1.0, low = 0.1, size = 5)
            self.Q[state] = np.full(5, -1000.0)
    
    def update_state_history(self, state, reward):
        self.state_history.append((state, reward))
    
    def learn(self, state, allowed_moves, reward_table, new_states, file):
        n = np.random.random()

        next_move = ""
        next_move_index = ""
        
        #print("allowed moves lol: {}".format(allowed_moves))

        if n < self.random_factor or np.all(self.Q[state] == self.Q[state][0]):
            next_move = np.random.choice(allowed_moves)
            next_move_index = ACTIONS[next_move][1]
            file.write("Possible moves: {}\n".format(allowed_moves))
            #for q_value in player.Q[state]:
            #    print("Q Value: {}".format(q_value))
            file.write("Possible Move Q Values: {}\n".format(self.Q[state]))
            file.write("Random Action: {}\n".format(next_move))
        else:
            file.write("Possible moves: {}\n".format(allowed_moves))
            #for q_value in player.Q[state]:
            #    print("Q Value: {}".format(q_value))
            file.write("Possible Move Q Values: {}\n".format(self.Q[state]))
            while next_move not in allowed_moves:
                next_move_index = np.argmax(self.Q[state])
                next_move = return_action(next_move_index)
            file.write("Selected Action: {}\n".format(next_move))
        
        
        reward = reward_table[state][next_move_index]
        new_state = new_states[next_move]
        max_next = np.max(self.Q[new_state])

        current_q_value = self.Q[state][next_move_index]
        new_q_value = float((1 - self.alpha) * current_q_value + self.alpha * (reward - 0.2 * max_next))
        self.Q[state][next_move_index] = new_q_value
        return next_move

    def update(self):
        if self.random_factor > 0.05:
            self.random_factor -= 10e-4
           
    def choose_action(self, state, allowed_moves, truck_level, customer, customer_level, reward_table):
        #print("Current state is {}".format(state))
        next_move = None
        current_reward = -10e15
        n = np.random.random()
        position = type_changer(state.split(' | ')[0])
        levels = type_changer(state.split(' | ')[1])
        if n < self.random_factor:
            next_move = np.random.choice(allowed_moves)
            #print("Random Action: {}".format(next_move))
        else:
            maxG = -10e15
            current_reward = maxG
            for action in allowed_moves:
                #print(action)
                index = ACTIONS[action][1]
                reward = reward_table[state][index]
                #print("Considering action {} for reward {}".format(action, reward))
                if reward > current_reward:
                    current_reward = reward
                    next_move = action
            #print("Selected Action: {}".format(next_move))
        return next_move
        