import numpy as np
from random import choice
from constants import *

"""
TODO:

Statics:
filled VS Unfilled

"""

class Enviroment:
    def __init__(self, grid_size):
        self.grid = np.full((grid_size, grid_size), 2)
        self.grid[1:-1, 1:-1] = PLAYFIELD
        self.grid_size = grid_size
        self.special_tiles = SpecialTiles(self)

        self.filled_percentage = 0
        self.instant_fill_increase = 0
        self.instant_player_died = False;

    """
    def is_cell_celltype(self, cell, celltype):

        grid[y][x] == PLAYFIELD: """

    def calculate_percentage(self, celltype):

        celltype_cells = self.find_cells(celltype)
        total_area = GRID_SIZE*GRID_SIZE

        self.filled_percentage = len(celltype_cells) / total_area
        #print("self.filled_percentage: ", self.filled_percentage)

    def find_cell(self, celltype):

        # search for a first replace point
        for row in range(self.grid_size):
            for column in range(self.grid_size):
                if self.grid[row][column] == celltype:
                    return [row, column]


    def find_cells(self, celltype):

        cell_list = []

        # search for a first replace point
        for row in range(self.grid_size):
            for column in range(self.grid_size):

                if self.grid[row][column] == celltype:
                    cell_list.append([row, column])

        return cell_list

    def within_grid(self, cell):

        r = cell[0]
        c = cell[1]

        if r < 0 or r >= self.grid_size:
            return False
        if c < 0 or c >= self.grid_size:
            return False

        return True

    # helper function
    def neighbours(self, r, c):
        """Calculates the neighbours of a given cell"""
        return [[r+1, c], [r, c+1], [r-1, c], [r, c-1],
                [r+1, c+1], [r+1, c-1], [r-1, c-1], [r-1, c+1]]

    def limited_neighbours(self, r, c):

        """Calculates the neighbours of a given cell"""
        return [[r+1, c], [r, c+1], [r-1, c], [r, c-1]]

    # can move to border
    def can_move(self, cell, celltype):

        moves = self.limited_neighbours(*cell) #cell[0], cell[1]
        #diagonal_moves =

        move_is_celltype = False

        for move in moves:

            if self.within_grid(move) and self.grid[move[0]][move[1]] == celltype:
                move_is_celltype = True

        return move_is_celltype

class SpecialTiles():

    def __init__(self, env):
        self.env = env
        self.cells = [] #
        self.generate_special_tiles()

    def generate_special_tiles(self):

        self.cells.clear()
        playfield_cells = self.env.find_cells(PLAYFIELD)
        #indexes = np.arange(playfield_cells.shape[0])
        num_specials = np.rint(len(playfield_cells) / 16 ).astype(np.int64)
        #specials = []

        for i in range(num_specials):
            cell = choice(playfield_cells)
            self.cells.append(cell)

        #return specials
