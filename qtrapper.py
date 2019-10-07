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
from random import randint, choice
import queue
from constants import *
from enviroment import *
from flood import *
from agent import Agent
from helperfunctions import *

models_file = open("models.npy","wb")
#models_file_read = open("models.npy","rb")

#loaded_q_table = np.load("models.npy")
## read with np.load(models_file) and set q_table with it?

#print(loaded_q_table)

ai_mode = False
speed = 10
game_won_percentage = 0.8
game_iterations = 100
show_plot = False

player_sprite = pygame.image.load('sprites/turtle.png');


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

        # enemy prototype
        self.enemy = Enemy()

        self.clock = pygame.time.Clock()
        self.env = Enviroment(grid_size)
        self.flood = Flood(self)

        self.game_won_percentage = game_won_percentage


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
        """
        Move player to nearest border using breadth-first search.
        """

        grid = game.env.grid

        if grid[self.y][self.x] == FILL:

            # print("move me plz")
            new_pos = game.env.find_cell(BORDER) # searches from topleft

            start_queue = queue.Queue()
            start_queue.put((self.x,self.y))
            BFS_results = BFS(start_queue, game, BORDER)
            #print("BFS_results: ", BFS_results)

            self.set_position(BFS_results)

    def check_collision(self, game):
        enemy = game.enemy
        grid = game.env.grid
        # Only check collisions when we have a lane
        if self.going_risky:
            for risk_pos in self.risky_lane:
                # If player risky lane collides with enemy
                if risk_pos[0] == enemy.y and risk_pos[1] == enemy.x:
                    # BFS search for where to move player
                    start_queue = queue.Queue()
                    start_queue.put((self.x,self.y))
                    BFS_results = BFS(start_queue, game, BORDER)
                    self.set_position(BFS_results)

                    # Mark all cells in risky_lane as playfield
                    for cell in self.risky_lane:
                        grid[cell[0]][cell[1]] = PLAYFIELD

                    self.risky_lane.clear()
                    break




class Enemy:
    def __init__(self):
        self.y = 15
        self.x = 10
        self.position = [self.y, self.x]
        self.direction = [1, 1]
        self.dir_list = [-1, 1]
        self.alive = True

    def update(self):
        print("updating")

    def move(self, game):
        """
        Moves straight until it hits a wall.
        """
        # print("moving")

        if self.alive == True:
            new_pos = [self.position[0] + self.direction[0], self.position[1] + self.direction[1]]
            if game.env.within_grid(new_pos):
                # Make sure new direction is a valid direction
                while game.env.grid[new_pos[0], new_pos[1]] == BORDER:
                    # self.direction = [choice(self.dir_list), choice(self.dir_list)]

                    # CHECK WHICH BORDER
                    if new_pos[0] == 0:  # TOP
                        self.direction = [-self.direction[0], self.direction[1]]
                    elif new_pos[1] == 0:  # LEFT
                        self.direction = [self.direction[0], -self.direction[1]]
                    elif new_pos[0] == GRID_SIZE - 1 :  # BOTTOM
                        self.direction = [-self.direction[0], self.direction[1]]
                    elif new_pos[1] == GRID_SIZE - 1:  # RIGHT
                        self.direction = [self.direction[0], -self.direction[1]]

                    new_pos = [self.position[0] + self.direction[0], self.position[1] + self.direction[1]]

                # Set the new position
                self.position = new_pos
                self.y = new_pos[0]
                self.x = new_pos[1]



def user_controller(event, game, agent):

    grid = game.env.grid
    player = game.player
    enemy = game.enemy

    if event.type == pygame.MOUSEBUTTONDOWN: # doesn't work rn since only keydown events are passed
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


def ai_controller(game, agent):

    cur_pos = copy.deepcopy(game.player.position)

    # new_pos = random_move(game)
    move = agent.ai_step()
    new_pos = [cur_pos[0] + move[0], cur_pos[1] + move[1]]

    # evaluate move and fill status
    filled_before = game.env.filled_percentage
    eval_move(game, new_pos, cur_pos)
    filled_after = game.env.filled_percentage

    # update instant fill increase value
    game.env.instant_fill_increase = 0
    if filled_after > filled_before:
        game.env.instant_fill_increase = filled_after - filled_before

# evaluate how the move changed the game and playfield status
def eval_move(game, new_pos, cur_pos):

    grid = game.env.grid
    player = game.player
    flood = game.flood

    y, x = new_pos

    if grid[y][x] == FILL:

        # if player can move to border
        if game.env.can_move(player.position, BORDER): # needed?
            # maybe cur_pos will be FILL?
            new_pos = cur_pos # or before again

    # if trapping an area
    if player.going_risky:

        # self-intersection. Handle this in a nice way?
        if grid[y][x] == RISKYLINE:
            intersection = True # do something with this

        # getting back to border
        if grid[y][x] == BORDER:
            player.going_risky = False

            # determin area etc
            flood.flood_area(player)
            game.env.calculate_percentage(FILL)

    # events on the playfield
    if grid[y][x] == PLAYFIELD: # and not going_risky:

        # when entering the playfield from border
        if not player.going_risky:
            player.going_risky = True

        grid[y][x] = RISKYLINE # fill risky line after player
        player.risky_lane.append([y, x])

    # the actual position update. For both AI and user controller
    player.set_position(new_pos)
    player.move_if_at_filled(game) # transport if player itself is trapped


def training_ai(agent):
    counter_games = 0

    score_plot = []
    counter_plot = []


    while counter_games < game_iterations:
        # print training progress
        if counter_games % 10 == 0:
            print("Iteration", counter_games)

        # Initialize classes
        game = Game(WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE, True)
        agent.init_agent(game)
        enemy = game.enemy
        # counter for enemy movement
        count_enemy = 0

        # Loop until the user clicks the close button.
        done = False
        steps_required = 0

        while not done:

            ai_controller(game, agent)

            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    done = True  # Flag that we are done so we exit this loop

            if game.env.filled_percentage >= game_won_percentage:
                done = True
                #print("GAME WON")
                #print(agent.q_table)

            if count_enemy % 10 == 0: # Remember to move to AI as well
                enemy.move(game)
            count_enemy += 1

            # Checking collisons
            game.player.check_collision(game) # Remember to move to AI as well

            steps_required += 1
            score_plot.append(steps_required)
            counter_plot.append(counter_games)

            draw_game(game)

            # Limit to 60 frames per second, then update the screen
            game.clock.tick(60)
            pygame.display.flip() # alternative: pygame.display.update()

            #print("game.score_plot", game.score_plot)
            #print("game.counter_plot", game.counter_plot)

        # one game done
        counter_games += 1
        agent.exploration_rate = agent.exploration_rate - 0.002 if agent.exploration_rate > 0.1 else agent.exploration_rate
        print("agent.exploration_rate", agent.exploration_rate)

    if show_plot == True:
        plot_seaborn(counter_plot, score_plot)

def draw_game(game):

    # Set the screen background
    game.gameDisplay.fill(DARKGRAY)
    grid = game.env.grid
    player = game.player
    enemy = game.enemy

    # Draw the grid
    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):

            if grid[row][column] == PLAYFIELD: # if risky line
                color = GRAY
            elif grid[row][column] == RISKYLINE: # if risky line
                color = BLUE
            elif grid[row][column] == BORDER: # if border
                color = DARKGREEN
            elif grid[row][column] == FILL: # if fill
                color = ORANGE

            # color the cell where the agent is
            #if row == player.y and column == player.x:
            #    color = GREEN

            # color enemy cells
            if row == enemy.y and column == enemy.x:
                color = DARKRED

            pygame.draw.rect(game.gameDisplay,
                             color,
                             [(MARGIN + WIDTH) * column + MARGIN,
                              (MARGIN + HEIGHT) * row + MARGIN,
                              WIDTH,
                              HEIGHT])


    player_blit_x = (MARGIN + WIDTH) * player.x + MARGIN/2
    player_blit_y = (MARGIN + HEIGHT) * player.y + MARGIN/2
    game.gameDisplay.blit(player_sprite, (player_blit_x, player_blit_y))


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
    enemy = game.enemy

    agent.init_agent(game)

    # Loop until the user clicks the close button.
    done = False

    # counter for enemy movement
    count_enemy = 0

    game.steps_required = 0

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

        if count_enemy % 10 == 0: # Remember to move to AI as well
            enemy.move(game)
        count_enemy += 1

        # Checking collisons
        game.player.check_collision(game) # Remember to move to AI as well

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



    #pygame.time.wait(5000) # pause before quit
    # If you forget this line, the program will 'hang' on exit.
    pygame.quit()


run()
