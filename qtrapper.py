"""
 Q-Trapper
 Sarol and Emmni jao

"""
"""
TODO:


count percentage of filled VS playfield cells - useful with a Grid class?
(fixed, but should be done earlier?) if agent is inside filled area -> move to closest borders

add:
actions
state
score

enemies

"""

import pygame
import numpy as np
import copy
from constants import *
from enviroment import *
from flood import *


class Game:

    def __init__(self, game_width, game_height, grid_size):
        pygame.display.set_caption('Q-Trapper')
        self.game_width = game_width
        self.game_height = game_height
        self.gameDisplay = pygame.display.set_mode((game_width, game_height+60))
        #self.bg = pygame.image.load("img/background.png")
        self.crash = False
        self.player = Player()
        self.score = 0

        self.clock = pygame.time.Clock()
        self.env = Enviroment(grid_size)


class Player(object):

    def __init__(self):

        self.y = 0
        self.x = 2
        self.position = [self.y, self.x]
        self.eaten = False
        self.y_change = 1
        self.x_change = 1

        self.going_risky = False
        self.risky_lane = []

    def update_position(self):

        self.position = [self.y, self.x]

    def update_xy(self):

        self.y = self.position[0]
        self.x = self.position[1]

def update_screen():

    pygame.display.update()


def run():

    pygame.init()
    counter_games = 0

    while counter_games < 1: # 150

        # Initialize classes
        game = Game(WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE)
        grid = game.env.grid
        player = game.player
        flood = Flood(game.env)

        # Loop until the user clicks the close button.
        done = False

        while not done:
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    done = True  # Flag that we are done so we exit this loop
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # User clicks the mouse. Get the position
                    # Change the x/y screen coordinates to grid coordinates
                    pos = pygame.mouse.get_pos()
                    column = pos[0] // (WIDTH + MARGIN)
                    row = pos[1] // (HEIGHT + MARGIN)

                    print("Click ", pos, "Grid coordinates: ", row, column)

                elif event.type == pygame.KEYDOWN:

                    keys = pygame.key.get_pressed()
                    prev_pos = copy.deepcopy(player.position) # [player.x, player.y] #Position(player.x,player.y) # copy.deepcopy(player) #



                    if keys[pygame.K_LEFT] and player.x > 0:
                        player.x -= 1

                    if keys[pygame.K_RIGHT] and player.x < GRID_SIZE - 1:
                        player.x += 1

                    if keys[pygame.K_UP] and player.y > 0:
                        player.y -= 1

                    if keys[pygame.K_DOWN] and player.y < GRID_SIZE - 1:
                        player.y += 1

                    player.update_position()


                    if grid[player.y][player.x] == FILL:
                        print("bumped into wall")

                        if game.env.can_move(player.position):
                            player.position = prev_pos
                        else:  # duplicate
                            print("cannot move")
                            player.position = game.env.find_cell(PLAYFIELD) # only one cell


                        player.update_xy()

                    if player.going_risky:

                        if grid[player.y][player.x] == RISKYLINE:

                            print("intersection!")

                        if grid[player.y][player.x] == BORDER:
                            player.going_risky = False
                            # print("going_safe!")

                            # determin area etc
                            flood.flood_area(player)

                    if grid[player.y][player.x] == PLAYFIELD: # and not going_risky:

                        if not player.going_risky:
                            player.going_risky = True
                            #print("going_risky!")

                        grid[player.y][player.x] = RISKYLINE # fill risky line after player
                        player.risky_lane.append([player.y, player.x])

            # Set the screen background
            game.gameDisplay.fill(DARKGRAY)

            # Draw the grid
            for row in range(GRID_SIZE):
                for column in range(GRID_SIZE):

                    if grid[row][column] == PLAYFIELD: # if risky line
                        color = GRAY
                    elif grid[row][column] == RISKYLINE: # if risky line
                        color = DARKRED
                    elif grid[row][column] == BORDER: # if border
                        color = DARKGREEN
                    elif grid[row][column] == FILL: # if fill
                        color = ORANGE

                    # color the cell where the agent is
                    if row == player.y and column == player.x:
                        color = GREEN

                    pygame.draw.rect(game.gameDisplay,
                                     color,
                                     [(MARGIN + WIDTH) * column + MARGIN,
                                      (MARGIN + HEIGHT) * row + MARGIN,
                                      WIDTH,
                                      HEIGHT])

            # Limit to 60 frames per second
            game.clock.tick(60)

            # Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            counter_games += 1

    # If you forget this line, the program will 'hang' on exit.
    pygame.quit()


run()
