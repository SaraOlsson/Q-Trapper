"""
Agent class
Sarol and Emmni jao
"""
import numpy as np
from constants import *

# Constants
NR_FEATURES = 4


class Agent:
    def __init__(self, game):
        self.q_table = np.zeros([2**NR_FEATURES, 4])
        self.features = np.zeros([NR_FEATURES])
        self.game = game
        self.actions = [[1, 0], [0, 1], [-1, 0], [0, -1]] # DOWN, RIGHT, UP, LEFT
        print(self.q_table)

    def get_is_celltype(self, cur_pos, action, celltype=PLAYFIELD):

        grid = self.game.env.grid
        print("cur pos", cur_pos)
        print("action", action)
        y = cur_pos[0] + action[0]
        x = cur_pos[1] + action[1]
        #y, x = cur_pos + action

        if grid[y][x] == celltype:
            return 1
        else:
            return 0

    def calculate_features(self):
        #print("calc features")
        cur_pos = self.game.player.position
        #print(cur_pos)
        idx = 0
        print("features before", self.features)
        for action in self.actions:
            self.features[idx] = self.get_is_celltype(cur_pos, action)
            idx += 1
        print("features after", self.features)


    def init_q_table(self, cur_):
        print("init q_table")
