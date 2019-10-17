"""
Agent class
Sarol and Emmni jao

TODO:
 write get_reward function
"""
import numpy as np
from constants import *
from helperfunctions import *
import random

# Constants
NR_FEATURES = 10 #10
MOVES = 4

# features
RISKY_LIM = 5 # not used now

"""
features

will action take player to:
- playfield(4)
- border (4)
- length of riskylane (1)
- is too close to enemy (1)

"""

class Agent:
    def __init__(self):
        self.q_table = np.zeros([2**NR_FEATURES, MOVES])
        print("q_table shape", self.q_table.shape)
        self.features = np.zeros([NR_FEATURES])
        self.game = None # game
        self.actions = [[1, 0], [0, 1], [-1, 0], [0, -1]] # DOWN, RIGHT, UP, LEFT
        self.cur_state = 0
        self.exploration_rate = 0.5
        self.exploration_rate_game = 0.1
        self.training = True
        self.learning_rate = 0.5
        self.gamma = 0.8

        # to count times we're in a specific state
        self.state_counter = np.zeros([2**NR_FEATURES])

        self.prev_action_index = 0;
        self.ping_pong_times = 0;
        self.current_reward = 0;
        #self.init_agent()
        #print(self.q_table)

    def exp_decay(self, epoch):
        initial_lrate = 0.5
        k = 0.005
        lrate = initial_lrate * np.exp(-k*epoch)
        return lrate

        # 0.1 = 0.5 * e^(-k*epoch)
        # 0.1 / 0.5 = e^(-k*epoch)
        # - np.log( 0.1 / 0.5) / 500 = k

    def init_agent(self, game):
        self.game = game
        self.calculate_features(self.game.player.position)
        self.get_state_from_features()

    # used for picking the best move
    def get_transition_reward(self, pos, move_idx):
        reward = 0

        grid = self.game.env.grid
        player = self.game.player
        y, x = pos # possible new position
        y_cur, x_cur = player.position
        y_prev, x_prev = player.prev_pos

        # negative reward if ping pong times
        if y == player.prev_pos[0] and x == player.prev_pos[1]:
            self.ping_pong_times += 1
            reward -= 2*self.ping_pong_times
            #print("ping_pong_times", self.ping_pong_times)
        else:
            self.ping_pong_times = 0
            #print("pos is prev_pos")

        # if action will close an area
        if grid[y][x] == BORDER and len(player.risky_lane) > RISKY_LIM:
            reward += 2

        border_dist_scores, min_dist = self.get_closest_to(pos, self.actions, BORDER)

        # play safe or be brave
        if player.enemy_too_close == 1:

            # pos reward for running away from enemy towards closest border
            if grid[y][x] == PLAYFIELD and border_dist_scores[move_idx] == 1:
                reward += 4

        else: # be brave

            # positive reward if keeping same direction
            if move_idx == self.prev_action_index:
                reward += 2

            # shouldnt walk too much on border
            if grid[y][x] == PLAYFIELD:
                reward += 1

        return reward

    # used when updating the q-table
    def get_reward(self, new_pos):

        reward = 0
        instant_fill = np.floor(self.game.env.instant_fill_increase*100) # eg from 0.01 to 1

        if self.game.env.instant_player_died == True:
            reward += -10 #20

        if instant_fill > 0:

            reward += 10

        reward -= 1

        self.current_reward = reward
        return reward


    # get best action index based on transition and reward
    def get_best_move(self, cur_pos):

        grid = self.game.env.grid
        # val should be based on qtable!
        q_values = self.q_table[self.cur_state]

        max = -np.inf
        best_index = -1
        idx = 0
        val = 0

        #print("enemy_too_close", self.game.player.enemy_too_close)

        for val in q_values:

            #print("value", val)

            move = self.actions[idx]
            temp_pos = [cur_pos[0] + move[0], cur_pos[1] + move[1]]

            if self.game.env.within_grid(temp_pos) and grid[temp_pos[0]][temp_pos[1]] != FILL:

                val += self.get_transition_reward(temp_pos, idx)
                if (val > max):
                    max = val
                    best_index = idx
                    #print("val > max")

            idx += 1

        return best_index

    def update_q_table(self, move_idx, cur_pos):

        cur_state = self.cur_state
        #print("cur_state FIRST", cur_state)
        new_pos = [cur_pos[0] + self.actions[move_idx][0], cur_pos[1] + self.actions[move_idx][1]]
        self.calculate_features(new_pos)
        #next_state = self.get_state_from_features() # is null juu
        self.get_state_from_features()
        next_state = self.cur_state

        # calculate q-vals
        cur_q_vals = [q_val for q_val in self.q_table[next_state]]

        max_q = np.max(cur_q_vals)

        # update table for this state and action
        old_q = self.q_table[cur_state][move_idx]
        new_q = old_q + self.learning_rate * (self.get_reward(new_pos) + self.get_transition_reward(new_pos, move_idx) + self.gamma * max_q - old_q) #
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
                    move_idx = random.randint(0, 3)
                else:
                    move_idx = self.get_best_move(cur_pos)
            else:
                if (random.uniform(0, 1) < self.exploration_rate_game):
                    move_idx = random.randint(0, 3)
                else:
                    move_idx = self.get_best_move(cur_pos)

            if move_idx < 0:
                print("move_idx < 0")
                continue

            move = self.actions[move_idx]
            self.prev_action_index = move_idx
            temp_pos = [cur_pos[0] + move[0], cur_pos[1] + move[1]]

            # check if temp_pos is within grid
            if self.game.env.within_grid(temp_pos) and self.game.env.grid[temp_pos[0]][temp_pos[1]] != FILL:
                break

        # update table
        self.update_q_table(move_idx, cur_pos)

        # get position after making a move
        cur_pos = [cur_pos[0] + self.actions[move_idx][0],
                   cur_pos[1] + self.actions[move_idx][1]]

        # calculate new features after the move
        self.calculate_features(cur_pos)
        self.get_state_from_features()

        self.state_counter[self.cur_state] += 1

        return self.actions[move_idx]

    def get_is_celltype(self, cur_pos, action, celltype=PLAYFIELD):

        grid = self.game.env.grid
        y = cur_pos[0] + action[0]
        x = cur_pos[1] + action[1]

        if self.game.env.within_grid([y, x]) and grid[y][x] == celltype:
            return 1
        else:
            return 0

    def get_is_close_enemy(self, min_dist = 0):

        if min_dist == 0: # not very meaningful if entering here
            too_close = 1 if self.game.player.closest_enemy_dist <= 2*TOO_CLOSE else 0
        else: # most useful
            too_close = 1 if self.game.player.closest_enemy_dist <= 2*min_dist else 0

        self.game.player.enemy_too_close = too_close

        return too_close

    def can_enter_border(self, celltype):

        player = self.game.player
        neighbour_cells = self.game.env.limited_neighbours(*player.position)

        for neighbour_cell in neighbour_cells:

            y, x = neighbour_cell
            if self.game.env.within_grid([y, x]) and self.game.env.grid[y][x] == celltype:
                return 1

        return 0

    def calculate_features(self, cur_pos):
        idx = 0

        for action in self.actions:
            self.features[idx] = self.get_is_celltype(cur_pos, action, BORDER)
            idx += 1

        self.features[idx] = len(self.game.player.risky_lane)
        idx += 1

        player_pos = self.game.player.position
        border_dist_scores, min_dist = self.get_closest_to(player_pos, self.actions, BORDER)

        self.features[idx] = self.get_is_close_enemy(min_dist)
        idx += 1

        for dist_binary_score in border_dist_scores:

            #print("dist_score", dist_score)
            self.features[idx] = dist_binary_score
            idx += 1


    # return binary feature scores for border surrounding check
    def get_closest_to(self, pos, actions, celltype):

        feature_scores = [0, 0, 0, 0]
        closest_actions = []
        min_dist = INF_DIST

        # calculate closest dist value
        for action in actions:

            distance = strict_direction_dist( self.game, pos, action, BORDER )
            if distance < min_dist:
                min_dist = distance

        # see which actions will lead to this min distance, change feature_score for then
        for i in range(len(actions)):

            action = actions[i]
            temp_pos = [pos[0] + action[0], pos[1] + action[1]]
            distance = strict_direction_dist( self.game, pos, action, BORDER )

            if self.game.env.within_grid(temp_pos) and distance == min_dist:
                closest_actions.append(action)
                feature_scores[i] = 1

        dir_names = list(map(action_to_dirname, closest_actions))
        #print("closest_actions", dir_names)
        #print("feature_scores", feature_scores)

        return feature_scores, min_dist


    def init_q_table(self, cur_):
        print("init q_table")

    def get_state_from_features(self):
        state_index = 0

        if (self.features[0] > 0): # 0-3: will action(s) lead to closest border
            state_index += 1
        if (self.features[1] > 0):
            state_index += 2
        if (self.features[2] > 0):
            state_index += 4
        if (self.features[3] > 0):
            state_index += 8
        if (self.features[4] > 0): # length of risky_lane
            state_index += 16
        if (self.features[5] > 0): # too close to enemy
            state_index += 32
        if (self.features[6] > 0):
            state_index += 64
        if (self.features[7] > 0):
            state_index += 128
        if (self.features[8] > 0):
            state_index += 256
        if (self.features[9] > 0):
            state_index += 512

        self.cur_state = state_index
