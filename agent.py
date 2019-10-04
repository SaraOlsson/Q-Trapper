"""
Agent class
Sarol and Emmni jao

TODO:
 write get_reward function
"""
import numpy as np
from constants import *
import random

# Constants
NR_FEATURES = 9


class Agent:
    def __init__(self):
        self.q_table = np.zeros([2**NR_FEATURES, 4])
        self.features = np.zeros([NR_FEATURES])
        self.game = None # game
        self.actions = [[1, 0], [0, 1], [-1, 0], [0, -1]] # DOWN, RIGHT, UP, LEFT
        self.cur_state = 0
        self.exploration_rate = 0.5
        self.exploration_rate_game = 0.1
        self.training = True
        self.learning_rate = 0.5
        self.gamma = 0.8
        #self.init_agent()
        print(self.q_table)

    def init_agent(self, game):
        self.game = game
        self.calculate_features(self.game.player.position)
        self.get_state_from_features()

    # used for picking the best move
    def get_transition_reward(self, pos):
        reward = 0

        grid = self.game.env.grid
        player = self.game.player
        y, x = pos

        if self.game.env.within_grid([y, x]):
            if grid[y][x] == PLAYFIELD:
                reward += 2
            elif grid[y][x] == BORDER:
                reward += 1
        else:
            reward -= 2
        if y == player.prev_pos[0] and x == player.prev_pos[1]:
            reward -= 2
            #print("pos is prev_pos")

        return reward

    # used when updating the q-table
    def get_reward(self, new_pos):

        #print("get_reward", self.game.env.instant_fill_increase)

        if self.game.env.instant_fill_increase > 0:
            #print("return 10")
            if self.game.env.instant_fill_increase >= 1: # funkar ev inte
                print("game won reward")
                return 50

            return 20

        return -1

        # if filled_percentage increased?

    # get best action index based on transition reward
    def get_best_move(self, cur_pos):
        max = -np.inf
        best_index = -1
        idx = 0
        val = 0

        for move in self.actions:
            temp_pos = [cur_pos[0] + move[0], cur_pos[1] + move[1]]

            val = self.get_transition_reward(temp_pos)
            if (val > max):
                max = val
                best_index = idx

            idx += 1
        return best_index

    def update_q_table(self, cur_state, move_idx, cur_pos):
        new_pos = [cur_pos[0] + self.actions[move_idx][0], cur_pos[1] + self.actions[move_idx][1]]
        self.calculate_features(new_pos)
        next_state = self.get_state_from_features()

        # calculate q-vals
        cur_q_vals = [q_val for q_val in self.q_table[next_state]]
        max_q = np.max(cur_q_vals)

        # update table for this state and action
        old_q = self.q_table[cur_state][move_idx]
        new_q = old_q + self.learning_rate * (self.get_reward(new_pos) + self.get_transition_reward(new_pos) + self.gamma * max_q - old_q)
        self.q_table[cur_state][move_idx] = new_q

    # each time step, first thing to do
    def ai_step(self):
        cur_pos = self.game.player.position
        # make random move when exploring
        move_idx = None
        move = None

        # get a move that is valid (within grid)
        while True:
            if self.training:
                if (random.uniform(0, 1) < self.exploration_rate):
                    # move_idx = np.floor(random.uniform(0, 1) * 4)  # 4 possible moves
                    move_idx = random.randint(0, 3)
                else:
                    move_idx = self.get_best_move(cur_pos)
            else:
                if (random.uniform(0, 1) < self.exploration_rate_game):
                    # move_idx = np.floor(random.uniform(0, 1) * 4)  # 4 possible moves
                    move_idx = random.randint(0, 3)
                else:
                    move_idx = self.get_best_move(cur_pos)

            move = self.actions[move_idx]
            temp_pos = [cur_pos[0] + move[0], cur_pos[1] + move[1]]

            # check if temp_pos is within grid
            if self.game.env.within_grid(temp_pos):
                break

        # update table
        self.update_q_table(self.cur_state, move_idx, cur_pos)

        # get position after making a move
        cur_pos = [cur_pos[0] + self.actions[move_idx][0],
                   cur_pos[1] + self.actions[move_idx][1]]

        # calculate new features after the move
        self.calculate_features(cur_pos)
        self.get_state_from_features()

        return self.actions[move_idx]

    def get_is_celltype(self, cur_pos, action, celltype=PLAYFIELD):

        grid = self.game.env.grid
        y = cur_pos[0] + action[0]
        x = cur_pos[1] + action[1]

        if self.game.env.within_grid([y, x]) and grid[y][x] == celltype:
            return 1
        else:
            return 0

    def calculate_features(self, cur_pos):
        idx = 0
        for action in self.actions:
            self.features[idx] = self.get_is_celltype(cur_pos, action)
            self.features[idx] = self.get_is_celltype(cur_pos, action, BORDER)
            idx += 1

        self.features[idx] = len(self.game.player.risky_lane)

    def init_q_table(self, cur_):
        print("init q_table")

    def get_state_from_features(self):
        state_index = 0
        if (self.features[0] > 0): # 0-3: is playfield
            state_index += 1
        if (self.features[1] > 0):
            state_index += 2
        if (self.features[2] > 0):
            state_index += 4
        if (self.features[3] > 0):
            state_index += 8
        if (self.features[4] > 0): # 0-3: is border
            state_index += 16
        if (self.features[5] > 0):
            state_index += 32
        if (self.features[6] > 0):
            state_index += 64
        if (self.features[7] > 0):
            state_index += 128
        if (self.features[8] > 10): # length of risky_lane
            state_index += 256
        self.cur_state = state_index
