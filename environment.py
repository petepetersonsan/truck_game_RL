import numpy as np
import pandas as pd
import math
import random
import itertools
import re

#make it so that every 3 moves a day passes and that's when the levels get updated.

ACTIONS = {'U': ((-1, 0), 0), 'D': ((1, 0), 1), 'L': ((0, -1), 2), 'R': ((0, 1), 3), 'I': ((0, 0), 4) }


## Levels are summarised on a 0 - 10 scale, 0 = Empty, 10 = Full.
def level_category(level, capacity):
    level_class = round(round(level / capacity, 1) * 5)
    if level > 0 and level_class == 0:
        level_class = 1
    return level_class

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

class restocking_game(object):
    def __init__(self, customer_input, customer_locations, truck_input, map_width, map_length):
        
        ## Customer initialisation, can either have default value or use input
        self.customers = customer_input
        self.customers_truck = dict.copy(self.customers)
        self.customers_truck[-1] = truck_input
        self.customer_locations = customer_locations
        
        ## Truck initialisation, can either have default value or use input
        self.truck_position = truck_input['Position']
        self.truck_capacity = truck_input['Capacity']
        self.truck_level = self.truck_capacity
        
        ## Map initialisation, can either default value or use input
        self.map = np.zeros([map_length, map_width])
        self.map[math.floor(map_length / 2), math.floor(map_width / 2)] = -1 ## Source
        
        for customer in self.customers:
            self.map[self.customers[customer]['Position']] = customer
            ## Below line shouldn't be necessary. 
            self.customers[customer]['Level'] = self.customers[customer]['Capacity']
            

        self.days = 0
        self.actions = 0
        self.allowed_states = None
        self.construct_allowed_states()
        self.reward_table = None
        self.construct_reward_table()
        
    def reset(self):
        
        ## Truck initialisation, can either have default value or use input
        self.truck_position = self.customers_truck[-1]['Position']
        self.truck_level = self.truck_capacity
        
        ## Map initialisation, can either default value or use input
        
        for customer in self.customers:
            self.customers[customer]['Level'] = self.customers[customer]['Capacity']
            

        self.days = 0
        self.actions = 0
        
    def is_allowed_move(self, state, action):
        y, x = state
        y += ACTIONS[action][0][0]
        x += ACTIONS[action][0][1]
        
        if y < 0 or x < 0 or y > len(self.map) - 1 or x > len(self.map[0]) - 1 or (action == 'I' and self.map[y, x] == 0):
            return False
        else:
            return True
        
    def construct_allowed_states(self):
        customers = list(self.customers_truck.keys())
        unique_combinations = []
        unique_combinations = list(list(zip(customers, element))
           for element in itertools.product(range(0, 6), repeat = len(customers)))
        allowed_states = {}
        for y, row in enumerate(self.map):
            for x, col in enumerate(row):
                position = (y, x)
                for combo in unique_combinations:
                    possible_actions = []
                    for action in ACTIONS:
                        if self.is_allowed_move(position, action):
                            possible_actions.append(action)
                    if len(possible_actions) == 0:
                        continue 
                    key = str(position) + " | " + str(combo)
                    allowed_states[key] = possible_actions
        self.allowed_states = allowed_states

    def construct_reward_table(self):
        reward_table = {}
        for state, actions in self.allowed_states.items():
            rewards = np.full(5, -10000)
            for action in actions:
                index = ACTIONS[action][1]
                position = type_changer(state.split(' | ')[0])
                levels = type_changer(state.split(' | ')[1])
                customer_level = ""
                customer_demand = ""
                customer_capacity = ""
                truck_level = ""
                if index < 4:
                    y, x = position
                    y += ACTIONS[action][0][0]
                    x += ACTIONS[action][0][1]
                    position = (y, x)
                else:
                    customer = self.get_customer(position)
                    if customer == -1:
                        for i in range(len(levels)):
                            if levels[i][0] == -1:
                                levels[i] = (-1, 5)
                    else:
                        for i in range(len(levels)):
                            if levels[i][0] == customer:
                                customer_capacity = self.customers[customer]['Capacity']
                                customer_level = (levels[i][1] / 5) * customer_capacity
                                customer_demand = customer_capacity - customer_level
                            elif levels[i][0] == -1:
                                truck_level = (levels[i][1] / 5) * self.truck_capacity
                        if customer_demand > truck_level:
                            customer_level += truck_level
                            truck_level = 0
                        else:
                            customer_level = customer_capacity
                            truck_level -= customer_demand
                        customer_state = level_category(customer_level, customer_capacity)
                        truck_state = level_category(truck_level, self.truck_capacity)
                        for i in range(len(levels)):
                            if levels[i][0] == customer:
                                levels[i] = (customer, customer_state)
                            elif levels[i][0] == -1:
                                levels[i] = (-1, truck_state)
                new_state = str(position) + ' | ' + str(levels)
                reward = (self.calculate_reward(new_state))
                rewards[index] = reward
            reward_table[state] = rewards
        self.reward_table = reward_table    

    def next_state(self, state, action):
        state = self.return_state()
        position = type_changer(state.split(' | ')[0])
        levels = type_changer(state.split(' | ')[1])
        index = ACTIONS[action][1]
        customer_level = ""
        customer_demand = ""
        customer_capacity = ""
        truck_level = ""
        if index < 4:
            y, x = position
            y += ACTIONS[action][0][0]
            x += ACTIONS[action][0][1]
            position = (y, x)
        else:
            customer = self.get_customer(position)
            if customer == -1:
                for i in range(len(levels)):
                    if levels[i][0] == -1:
                        levels[i] = (-1, 5)
            else:
                for i in range(len(levels)):
                    if levels[i][0] == customer:
                        customer_capacity = self.customers[customer]['Capacity']
                        customer_level = (levels[i][1] / 5) * customer_capacity
                        customer_demand = customer_capacity - customer_level
                    elif levels[i][0] == -1:
                        truck_level = (levels[i][1] / 5) * self.truck_capacity
                if customer_demand > truck_level:
                    customer_level += truck_level
                    truck_level = 0
                else:
                    customer_level = customer_capacity
                    truck_level -= customer_demand
                customer_state = level_category(customer_level, customer_capacity)
                truck_state = level_category(truck_level, self.truck_capacity)
                for i in range(len(levels)):
                    if levels[i][0] == customer:
                        levels[i] = (customer, customer_state)
                    elif levels[i][0] == -1:
                        levels[i] = (-1, truck_state)
        new_state = str(position) + ' | ' + str(levels)
        return new_state        


    def update_levels(self):
        ## Stock levels update
        for customer in self.customers:
            usage = (random.randint(0, 50) * 0.01 ) * self.customers[customer]['Capacity']
            if usage > self.customers[customer]['Level']:
                self.customers[customer]['Level'] = 0
            else:
                self.customers[customer]['Level'] -= usage
        self.days += 1
    
    def return_state(self):
        levels = []
        for customer in self.customers:
            levels.append((customer, level_category(self.customers[customer]['Level'], self.customers[customer]['Capacity'])))
        levels.append((-1, level_category(self.truck_level, self.truck_capacity)))
        state = str(self.truck_position) + " | " + str(levels)
        return state
                
    def take_action(self, action):
        
        ## Movement Update
        if action in ('U', 'D', 'L', 'R'):
            y, x = self.truck_position
            y += ACTIONS[action][0][0]
            x += ACTIONS[action][0][1]
            if y < 0 or x < 0 or x > len(self.map[0]) - 1 or y > len(self.map) - 1:
                return "Invalid Move"
            else:
                self.truck_position = (y, x)
        
        
        ## Fill / Reload Update
        else:
            customer = self.get_customer(self.truck_position)
            if customer == -1:
                self.truck_level = self.truck_capacity
            else:
                customer_demand = self.customers[customer]['Capacity'] - self.customers[customer]['Level']
                if customer_demand < self.truck_level:
                    self.customers[customer]['Level'] = self.customers[customer]['Capacity']
                    self.truck_level -= customer_demand
                else:
                    self.customers[customer]['Level'] += self.truck_level
                    self.truck_level = 0
        self.actions += 1
    
    def calculate_reward(self, state):
        reward = 0
        
        ## Reward should have something to do with where the truck's location is compared to customers / source.
        ## Should be worse the further the truck is and this should be scaled by the customer / truck's level.
        ## e.g. Truck is 5 squares away from customer 1. If customer level is High, this reward part is -1 * 5 = -5. 
        ## If customer level is Low, this is -3 * 5 etc. 

        position = type_changer(state.split(' | ')[0])
        levels = type_changer(state.split(' | ')[1])
        #print("\n")
        #print(state)
        for i in range(len(levels)):
            customer = levels[i][0]
            level_state = levels[i][1]
            if customer == -1:
                x_distance = abs(position[0] - 2)
                y_distance = abs(position[1] - 2)
                distance = x_distance + y_distance
            else:
                x_distance = abs(position[0] - self.customers[customer]['Position'][0])
                y_distance = abs(position[1] - self.customers[customer]['Position'][1])
                distance = x_distance + y_distance
            if distance == 0:
                reward_part = 0.1
            else:
                reward_part = (5 - level_state) * -1 * (3 * math.log(distance) + 1)
        #    print("Customer {} at position {} has reward {}".format(customer, self.customers_truck[customer]['Position'], reward_part))
            reward += reward_part
        #print("Total reward is {}".format(reward))
        return reward
        
    
    def get_state_and_reward(self):
        return self.return_state(), self.calculate_reward(self.return_state())

    def get_customer(self, position):
        customer = round(self.map[position])
        if customer == 0:
            return None
        else:
            return customer

    def get_customer_level(self):
        customer = self.get_customer(self.truck_position)
        if customer == None:
            return None
        else:
            return self.customers_truck[customer]['Level']
    
    
    ## Game over if all customers are empty :(
    def is_game_over(self):
        empty_count = 0
        for customer in self.customers:
            if self.customers[customer]['Level'] == 0:
                empty_count += 1
        
        if empty_count == len(self.customers):
            return True
        else:
            return False