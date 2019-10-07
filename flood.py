import copy
from constants import *

class Flood():

    def __init__(self, game):

        self.game = game
        self.env = game.env
        self.grid = game.env.grid
        self.smallest_area = []
        self.current_area = []
        self.visited = []
        self.to_visit = game.env.find_cells(PLAYFIELD)


    def init_flood(self):

        self.smallest_area.clear()
        self.current_area.clear()
        self.visited.clear()

        self.to_visit.clear()
        self.to_visit = self.env.find_cells(PLAYFIELD)


    def flood_area(self, player):

        #while(len(self.to_visit) > 0):

        self.init_flood()
        grid = self.env.grid

        num_areas = 0

        test = self.env.find_cells(PLAYFIELD)

        for idx in range(2): # should catch all areas..
            flood_starting_point = self.find_flood_starting_point(celltype = PLAYFIELD)
            #print("flood_starting_point", flood_starting_point)

            if flood_starting_point:

                self.current_area.clear()
                self.flood_fill(*flood_starting_point, celltype = PLAYFIELD)
                num_areas += 1

                if len(self.current_area) < len(self.smallest_area):
                    self.smallest_area.clear();
                    self.smallest_area = copy.copy(self.current_area)
                elif len(self.smallest_area) == 0: # if it was the first area calculated
                    self.smallest_area = copy.copy(self.current_area)

            else: # if agent was walking along border (no explcit area)
                if num_areas == 1: # if it was the first area calculated
                    self.smallest_area = copy.copy(player.risky_lane)

        self.update_grid_values(player)

    def find_if_enemy(self, cell, enemy_list):
        ##print("find_if_enemy")
        enemy = self.game.enemy
        r, c = cell
        # get neighbours of cell
        fill_neighbours = self.env.neighbours(r, c)
        # is one of the neighbours an enemy?
        for neighbour in fill_neighbours:

            n_r, n_c = neighbour
            if n_r == enemy.y and n_c == enemy.x and neighbour not in enemy_list:
                #print("enemy trapped at", neighbour)
                enemy.alive = False
                enemy_list.append(neighbour)
                # return True

    def update_grid_values(self, player):

        grid = self.env.grid
        enemy = self.game.enemy
        found = False
        enemy_list = []

        # fill enclosured are to no mans land
        for cell in self.smallest_area:

            r, c = cell
            grid[r][c] = FILL

            self.find_if_enemy(cell, enemy_list )

        # check now if there is still > 1 area

        # fill risky lane to border
        for cell in player.risky_lane:
            grid[cell[0]][cell[1]] = BORDER

        player.risky_lane.clear()

        # fill borders without playfield as neighbor to no mans land
        border_cells = self.env.find_cells(BORDER)
        for cell in border_cells:

            moves = self.env.neighbours(*cell) #cell[0], cell[1]
            move_is_playfield = False

            for move in moves:

                if self.env.within_grid(move) and grid[move[0]][move[1]] == PLAYFIELD:
                    move_is_playfield = True

            if move_is_playfield == False:
                grid[cell[0]][cell[1]] = FILL

        # chech whether there is an enemy trapped!


    # reqursive
    def flood_fill(self, r, c, celltype):
        grid = self.env.grid
        enemy = self.game.enemy

        #if r == enemy.y and c == enemy.x:
        #    print("enemy trapped")

        if r < 0 or r >= GRID_SIZE: return
        if c < 0 or c >= GRID_SIZE: return
        if grid[r][c] != celltype:
            return

        self.current_area.append([r, c]) # will be cleared before each flood_fill
        self.visited.append([r, c])

        moves = self.env.neighbours(r, c) # limited_
        for move in moves:
            if move not in self.visited:
                self.flood_fill(move[0], move[1], celltype)

    def find_flood_starting_point(self, celltype = PLAYFIELD):
        grid = self.env.grid
        for row in range(GRID_SIZE):
            for column in range(GRID_SIZE):
                if grid[row][column] == celltype and [row, column] not in self.visited:
                    return [row, column]
