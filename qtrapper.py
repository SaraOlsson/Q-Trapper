"""
 Q-Trapper
 Sarol and Emmni jao

"""
"""
TODO:

add:
actions
state
score

enemies

Game structure:
(started) AI or user controller

"""

import pygame
import numpy as np
import copy
from random import randint
from constants import *
from enviroment import *
from flood import *
from agent import Agent
import queue
from helperfunctions import *

models_file = open("models.npy","wb")
#models_file_read = open("models.npy","rb")

#loaded_q_table = np.load("models.npy")
## read with np.load(models_file) and set q_table with it?

#print(loaded_q_table)

ai_mode = True
speed = 10
game_won_percentage = 0.8
game_iterations = 3

class Game:

    def __init__(self, game_width, game_height, grid_size, show=False):
        if show:
            pygame.display.set_caption('Q-Trapper')
            self.game_width = game_width
            self.game_height = game_height
            self.gameDisplay = pygame.display.set_mode((game_width, game_height+60))
        #self.bg = pygame.image.load("img/background.png")
        self.crash = False
        self.player = Player()
        self.score = 0
        self.steps_required = 0

        self.clock = pygame.time.Clock()
        self.env = Enviroment(grid_size)
        self.flood = Flood(self.env)

class Player(object):

    def __init__(self):

        self.y = 0
        self.x = 2
        self.position = [self.y, self.x]
        self.prev_pos = [self.y, self.x]
        self.eaten = False
        self.y_change = 1
        self.x_change = 1

        self.going_risky = False
        self.risky_lane = []

    def set_position(self, new_pos):

        self.prev_pos = copy.copy(self.position)
        self.y, self.x = new_pos
        self.position = [self.y, self.x]

    def move_if_at_filled(self, game):

        grid = game.env.grid

        if grid[self.y][self.x] == FILL:

            # print("move me plz")
            new_pos = game.env.find_cell(BORDER) # searches from topleft

            start_queue = queue.Queue()
            start_queue.put((self.x,self.y))
            BFS_results = BFS(start_queue, game, BORDER)
            #print("BFS_results: ", BFS_results)

            self.set_position(BFS_results)

def user_controller(event, game, agent):

    grid = game.env.grid
    player = game.player

    if event.type == pygame.MOUSEBUTTONDOWN:
        # User clicks the mouse. Get the position
        # Change the x/y screen coordinates to grid coordinates
        pos = pygame.mouse.get_pos()
        column = pos[0] // (WIDTH + MARGIN)
        row = pos[1] // (HEIGHT + MARGIN)

        print("Click ", pos, "Grid coordinates: ", row, column)

    elif event.type == pygame.KEYDOWN:

        keys = pygame.key.get_pressed()
        cur_pos = copy.deepcopy(player.position)

        move_array = [0, 0]
        y_change = 0
        x_change = 0

        if keys[pygame.K_LEFT] and player.x > 0:
            x_change = -1

        if keys[pygame.K_RIGHT] and player.x < GRID_SIZE - 1:
            x_change = 1

        if keys[pygame.K_UP] and player.y > 0:
            y_change = -1

        if keys[pygame.K_DOWN] and player.y < GRID_SIZE - 1:
            y_change = 1

        y = player.y + y_change
        x = player.x + x_change

        new_pos = [y, x]

        eval_move(game, new_pos, cur_pos)


def random_move(game):

    pos_changes = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    #moves = [[-1, 0], [0, -1]]
    safe_moves = []
    player = game.player

    for pos_change in pos_changes:

        y = player.y + pos_change[0]
        x = player.x + pos_change[1]
        move = [y,x]

        if game.env.within_grid(move):
            safe_moves.append(move)
            # print("safe move: ", move )

    rand_ind = randint(0, len(safe_moves) - 1)
    return safe_moves[rand_ind]

def ai_controller(game, agent):

    # naive first code:
    # get random value 0: left, 1:right, 2:up, 3:down
    cur_pos = copy.deepcopy(game.player.position)

    # new_pos = random_move(game)
    move = agent.ai_step()
    new_pos = [cur_pos[0] + move[0], cur_pos[1] + move[1]]

    # update player position
    eval_move(game, new_pos, cur_pos)


def eval_move(game, new_pos, cur_pos):

    grid = game.env.grid
    player = game.player
    flood = game.flood

    y, x = new_pos

    if grid[y][x] == FILL:
        #print("bumped into wall")

        # if player can move to border
        if game.env.can_move(player.position, BORDER):
            # maybe cur_pos will be FILL?
            new_pos = cur_pos # or before again
        """
        else:  # if cannot move at all
            # print("cannot move buhu")
            new_pos = game.env.find_cell(BORDER) # only one cell
            player.set_position(new_pos)
            y, x = new_pos """

    if player.going_risky:

        if grid[y][x] == RISKYLINE:

            temp = 0
            #print("intersection!")

        if grid[y][x] == BORDER:
            player.going_risky = False
            # print("going_safe!")

            # determin area etc
            flood.flood_area(player)
            game.env.calculate_percentage(FILL)


    if game.env.within_grid([y, x]) and grid[y][x] == PLAYFIELD: # and not going_risky:

        if not player.going_risky:
            player.going_risky = True
            #print("going_risky!")

        grid[y][x] = RISKYLINE # fill risky line after player
        player.risky_lane.append([y, x])

    player.set_position(new_pos)
    player.move_if_at_filled(game)


def training_ai(agent):
    counter_games = 0

    while counter_games < game_iterations:
        # print training progress
        if counter_games % 10 == 0:
            print("Iteration", counter_games)

        # Initialize classes
        game = Game(WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE)

        agent.init_agent(game)

        # Loop until the user clicks the close button.
        done = False

        while not done:

            if ai_mode == True:
                ai_controller(game, agent)

            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    done = True  # Flag that we are done so we exit this loop

                if event.type == pygame.KEYDOWN and ai_mode == False:
                    print(event.type)
                    user_controller(event, game, agent)


            if game.env.filled_percentage >= game_won_percentage:
                done = True
                #print("GAME WON")
                #print(agent.q_table)

        # one game done
        counter_games += 1

def draw_game(game):

    # Set the screen background
    game.gameDisplay.fill(DARKGRAY)
    grid = game.env.grid
    player = game.player

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


def run():

    pygame.init()

    agent = Agent()

    if ai_mode == True:
        # Train AI off screen
        training_ai(agent)

    # After training, use agent to play the game
    agent.training = False

    # Initialize classes
    game = Game(WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE, True)

    agent.init_agent(game)

    # Loop until the user clicks the close button.
    done = False

    while not done:

        if ai_mode == True:
            ai_controller(game, agent)
            pygame.time.wait(speed)

        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop

            if event.type == pygame.KEYDOWN and ai_mode == False:
                # print(event.type)
                user_controller(event, game, agent)

        if game.env.filled_percentage >= game_won_percentage:
            done = True
            print("GAME WON")
            print(agent.q_table)
            print("steps_required", game.steps_required)

        draw_game(game)

        # Limit to 60 frames per second, then update the screen
        game.clock.tick(60)
        pygame.display.flip() # alternative: pygame.display.update()
        game.steps_required += 1

    #to_save = np.arange(10)
    np.save("models", agent.q_table)


    # If you forget this line, the program will 'hang' on exit.
    pygame.quit()


run()
