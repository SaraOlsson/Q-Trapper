import numpy as np
from constants import *

"""
TODO:

Statics:
filled VS Unfilled

"""

class Enviroment:
    def __init__(self, grid_size):
        self.grid = np.full((grid_size, grid_size), 2)
        self.grid[1:-1, 1:-1] = 0
        self.grid_size = grid_size

        self.filled_percentage = 0

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


    def can_move(self, cell):

        moves = self.limited_neighbours(*cell) #cell[0], cell[1]
        #diagonal_moves =

        move_is_playfield = False

        for move in moves:

            if self.within_grid(move) and self.grid[move[0]][move[1]] == BORDER:
                move_is_playfield = True

        return move_is_playfield
