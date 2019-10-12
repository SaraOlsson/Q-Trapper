"""
 Q-Trapper
 Sarol and Emmni jao

"""

import pygame
import numpy as np
import copy
from random import randint, choice, uniform
import queue
from constants import *
from enviroment import *
from flood import *
from agent import *
from helperfunctions import *

# models_file = open("models.npy","wb")

ai_mode = True
speed = 20
game_won_percentage = 0.8
game_iterations = 0
show_plot = False
show_training = False

replay_mode = True # () user input)

# file options
save_q_table = False
load_q_table = True
from_scratch = False # continue on loaded q-table

player_sprite = pygame.image.load('sprites/turtle_up.png');
playfield_sprite = pygame.image.load('sprites/water.png');
playfield_special_sprite = pygame.image.load('sprites/water_light_wave2.png');
enemy_sprite = pygame.image.load('sprites/shark.png');
enemy_dead_sprite = pygame.image.load('sprites/gravestone.png');
border_sprite = pygame.image.load('sprites/shallow_beach.png');
riskyline_sprite = pygame.image.load('sprites/risky_water.png');
fill_sprite = pygame.image.load('sprites/beach.png');

# number of enemies
num_enemies_training = 2
num_enemies_game = 2

# visual appearence
draw_tiles = True

class Game:

    def __init__(self, game_width, game_height, grid_size, show=False, num_enemies=1):
        if show:
            pygame.display.set_caption('Q-Trapper')
            self.game_width = game_width
            self.game_height = game_height
            self.gameDisplay = pygame.display.set_mode((game_width, game_height+60))
        #self.bg = pygame.image.load("img/background.png")
        self.crash = False
        self.player = Player()
        #self.score = 0
        self.steps_required = 0
        self.lifes_gone = 0

        # enemies prototype
        self.enemies = []
        for n in range(num_enemies):
            self.enemies.append(Enemy())

        self.clock = pygame.time.Clock()
        self.env = Enviroment(grid_size)
        self.flood = Flood(self)

        self.game_won_percentage = game_won_percentage

    def add_enemy(self, pos):

        self.enemies.append(Enemy(pos))


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
        self.pos_before_risky = self.position
        self.risky_lane = []
        self.prev_risky_length = 0

        self.closest_enemy_dist = INF_DIST
        self.latest_enemy_dist = 0
        self.steps_at_border = 0

        # DOWN, RIGHT, UP, LEFT
        self.player_sprites = [pygame.image.load('sprites/turtle_down.png'),
                              pygame.image.load('sprites/turtle_right.png'),
                              pygame.image.load('sprites/turtle_up.png'),
                              pygame.image.load('sprites/turtle_left.png')]

        self.sprite_idx = 1

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

            #print("move me plz")
            # new_pos = game.env.find_cell(BORDER) # searches from topleft
            #
            # start_queue = queue.Queue()
            # start_queue.put((self.x,self.y))
            # BFS_results = BFS(start_queue, game, BORDER)
            #print("BFS set_position: ", BFS_results)
            #print("searching")
            rows, columns = np.where(grid == BORDER)
            border_cells = np.stack((rows, columns), axis=1)
            closest_border = self.position
            #print('heeeeej')
            if (border_cells.shape[0] != 0):
            #     print(grid)
            #     print(rows)
            #     print(columns)
            # print("border_cells", border_cells.shape)
                _, closest_border = calculate_distance_to_cells(self, border_cells)


            self.set_position(closest_border)

    def check_collisions(self, game):
        enemies = game.enemies
        grid = game.env.grid

        game.env.instant_player_died = False

        # Only check collisions when we have a lane
        if self.going_risky:
            for risk_pos in self.risky_lane:
                # Check for all enemies
                for enemy in enemies:
                    # If player risky lane collides with enemy
                    if enemy.alive == True and risk_pos[0] == enemy.y and risk_pos[1] == enemy.x:

                        game.lifes_gone += 1

                        # set position to where the player left the border
                        new_pos = [self.pos_before_risky[0], self.pos_before_risky[1]]
                        self.set_position(new_pos)
                        game.env.instant_player_died = True
                        # print("enemy position: ", self.position)


                        # Mark all cells in risky_lane as playfield
                        for cell in self.risky_lane:
                            grid[cell[0]][cell[1]] = PLAYFIELD

                        self.risky_lane.clear()
                        break


class Enemy:
    def __init__(self, pos = None):

        self.y = randint(2, 18) if pos is None else pos[0]
        self.x = randint(2, 18) if pos is None else pos[1]
        self.position = [self.y, self.x] if pos is None else pos
        # Initialize with random direction
        self.dir_list = [[1, 1], [-1, -1], [-1, 1], [1, -1]]
        self.direction = choice(self.dir_list)
        self.dir_list_2 = [-1, 1]
        self.alive = True

    def set_position(self, new_pos):

        self.prev_pos = copy.copy(self.position)
        self.y, self.x = new_pos
        self.position = [self.y, self.x]

    def update(self):
        print("updating")

    def move(self, game):
        """
        Moves straight until it hits a wall.
        """
        # print("moving")

        if self.alive == True:
            new_pos = [self.position[0] + self.direction[0], self.position[1] + self.direction[1]]

            # set_new_pos = True
            if game.env.within_grid(new_pos):

                if game.env.grid[new_pos[0]][new_pos[1]] == BORDER:
                    try_counter = 0

                    while True:

                        # decide if top, bottom, left or right and bounce
                        new_dir = get_new_enemy_dir(self.direction, self.position, new_pos, game)

                        # RANDOMNESS
                        # if new_dir == [-5,-5]: # unvalid
                        #     print("new_dir is None")
                        #     self.direction = [choice(self.dir_list_2), choice(self.dir_list_2)]
                        # else:
                        #     self.direction = new_dir
                        # new_pos = [self.position[0] + self.direction[0], self.position[1] + self.direction[1]]

                        self.direction = new_dir
                        new_pos = [self.position[0] + self.direction[0], self.position[1] + self.direction[1]]

                        # check if new_pos is within grid
                        if game.env.within_grid(new_pos) and game.env.grid[new_pos[0]][new_pos[1]] != BORDER:
                            #print("new_pos: ", new_dir)
                            break

                        try_counter += 1

                        if try_counter > 3:
                            #print("enemy is trapped")
                            self.alive = False
                            #set_new_pos = False
                            #break
                            return # leave function
            else:
                print("BUG: enemy new_pos is ", new_pos)
                return # shouldn't be here though

            #if set_new_pos == True:
            self.position = new_pos
            self.y = new_pos[0]
            self.x = new_pos[1]

            self.dist_to_risky_lane(game)

    # TODO is enemy moving toward player or away from?
    # find closest distance from this enemy to riskylane
    def dist_to_risky_lane(self, game):

        player = game.player
        min_dist = INF_DIST
        if len(player.risky_lane) > 0:
            min_dist, _ = calculate_distance_to_cells(self, player.risky_lane)

        # update closest_enemy_dist if a riskyline currently exists and was smaller than for any other enemy
        if min_dist < INF_DIST:
            #print("enemy at distance", min_dist, "from riskyline")
            player.latest_enemy_dist = player.closest_enemy_dist
            player.closest_enemy_dist = min_dist if min_dist < player.closest_enemy_dist else player.closest_enemy_dist


# event.type = KEYDOWN:
def user_controller(event, game, agent):

    grid = game.env.grid
    player = game.player
    enemies = game.enemies

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

    # change sprite idx
    step_made = [new_pos[0]-cur_pos[0], new_pos[1]-cur_pos[1]]
    step_list = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    player.sprite_idx = step_list.index(step_made) if step_made in step_list else 1 # sprite_idx is gobal

    if grid[y][x] == FILL:

        print("should not happend with AI controller")

        # if player can move to border
        if game.env.can_move(player.position, BORDER): # needed?
            # maybe cur_pos will be FILL?
            new_pos = cur_pos # or before again

    # if trapping an area
    if player.going_risky:

        # self-intersection. Handle this in a nice way?
        if grid[y][x] == RISKYLINE:

            # find index of intersection
            intersection_idx = None
            for i in range(len(player.risky_lane)):
                if player.risky_lane[i][0] == y and player.risky_lane[i][1] == x:
                    intersection_idx = i
                    break

            # Set rest of list to playfield
            for rp in player.risky_lane[intersection_idx+1:]:
                grid[rp[0]][rp[1]] = PLAYFIELD

            # remove rest of list
            results = [player.risky_lane[idx] for idx in range(len(player.risky_lane)) if idx <= intersection_idx]
            player.risky_lane = results

            intersection = True # do something with this

        # getting back to border
        if grid[y][x] == BORDER:
            #print("BORDER")
            player.going_risky = False

            # check if the player has only just left border
            #print(player.risky_lane)
            if len(player.risky_lane) == 1:
                # count neighbours that are playfield
                neighbours = game.env.limited_neighbours(cur_pos[0], cur_pos[1])
                count_playfield = 0

                for n in neighbours:
                    if grid[n[0]][n[1]] == PLAYFIELD:
                        count_playfield += 1

                # if three or more neighbours are playfield, the line is invalid
                #print(count_playfield)
                if count_playfield >= 3:
                    rp = player.risky_lane[0]
                    grid[rp[0]][rp[1]] = PLAYFIELD
                    player.risky_lane = []

            # determine area etc
            flood.flood_area(player)
            game.env.calculate_percentage(FILL)

    # events on the playfield
    if grid[y][x] == PLAYFIELD: # and not going_risky:

        # when entering the playfield from border
        if not player.going_risky:
            player.going_risky = True
            player.pos_before_risky = cur_pos


        grid[y][x] = RISKYLINE # fill risky line after player
        player.prev_risky_length = len(player.risky_lane)
        player.risky_lane.append([y, x])

    if grid[y][x] == BORDER:
        player.steps_at_border += 1
    else:
        player.steps_at_border = 0

    # the actual position update. For both AI and user controller
    player.set_position(new_pos)
    player.move_if_at_filled(game) # transport if player itself is trapped


def training_ai(agent):

    counter_games = 0

    # for plotting statistics
    reward_plot = []
    score_plot = []
    counter_plot = []
    lifes_plot = []

    # run the game several times
    while counter_games < game_iterations:
        # print training progress
        if counter_games % 10 == 0:
            print("Iteration", counter_games)

        # Initialize classes
        game = Game(WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE, show_training, num_enemies_training)
        agent.init_agent(game)
        enemies = game.enemies
        # counter for enemies movement
        count_enemy = 0

        # Loop until the user clicks the close button.
        done = False
        game.steps_required = 0
        total_reward = 0

        # ONE GAME
        while not done:

            ai_controller(game, agent)

            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    done = True  # Flag that we are done so we exit this loop

            if game.env.filled_percentage >= game_won_percentage:
                done = True
                #print("GAME WON")
                #print(agent.q_table)

            game.player.closest_enemy_dist = INF_DIST

            #if count_enemy % 10 == 0: # Remember to move to AI as well
            for enemy in enemies:
                enemy.move(game)
            count_enemy += 1

            # Checking collisons
            game.player.check_collisions(game) # Remember to move to AI as well

            game.steps_required += 1
            total_reward += agent.current_reward

            if show_training == True:
                draw_game(game)

                # Limit to 60 frames per second, then update the screen
                pygame.time.wait(speed)
                game.clock.tick(60)
                pygame.display.flip() # alternative: pygame.display.update()


        # Update statistics
        score_plot.append(game.steps_required)
        reward_plot.append(total_reward)
        counter_plot.append(counter_games)
        lifes_plot.append(game.lifes_gone)

        # one game done
        counter_games += 1
        agent.exploration_rate = agent.exploration_rate - 0.002 if agent.exploration_rate > 0.1 else agent.exploration_rate
        #print("agent.exploration_rate", agent.exploration_rate)

    if show_plot == True:

        plot_seaborn(counter_plot, reward_plot, 'game iteration', 'total reward' )
        plot_seaborn(counter_plot, lifes_plot, 'game iteration', 'lifes gone' )
        plot_seaborn(counter_plot, score_plot, 'game iteration', 'steps required' )

# is called every time step
def draw_game(game):

    # Set the screen background
    game.gameDisplay.fill(DARKGRAY)
    grid = game.env.grid
    player = game.player
    enemies = game.enemies

    if (game.steps_required % 100 == 0 or game.steps_required == 1):
        game.env.special_tiles.generate_special_tiles()

    # Draw the grid
    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):

            if grid[row][column] == PLAYFIELD: # if risky line

                color = GRAY

                if [row, column] in game.env.special_tiles.cells:
                    sprite = playfield_special_sprite
                else:
                    sprite = playfield_sprite

            elif grid[row][column] == RISKYLINE: # if risky line
                color = BLUE
                sprite = riskyline_sprite

            elif grid[row][column] == BORDER: # if border
                color = DARKGREEN
                sprite = border_sprite

            elif grid[row][column] == FILL: # if fill
                color = ORANGE
                sprite = fill_sprite

            # color enemy cells
            for enemy in enemies:
                if row == enemy.y and column == enemy.x:
                    if enemy.alive == True:
                        color = DARKRED
                    else:
                        color = BLACK

            if draw_tiles == True:

                blit_x = (MARGIN + WIDTH) * column + MARGIN/2
                blit_y = (MARGIN + HEIGHT) * row + MARGIN/2
                game.gameDisplay.blit(sprite, (blit_x, blit_y))

                # blit enemy cells
                for enemy in enemies:
                    if row == enemy.y and column == enemy.x:
                        if enemy.alive == True:
                            game.gameDisplay.blit(enemy_sprite, (blit_x, blit_y))
                        else:
                            game.gameDisplay.blit(enemy_dead_sprite, (blit_x, blit_y))


            else:

                pygame.draw.rect(game.gameDisplay,
                                 color,
                                 [(MARGIN + WIDTH) * column + MARGIN,
                                  (MARGIN + HEIGHT) * row + MARGIN,
                                  WIDTH,
                                  HEIGHT])


    player_blit_x = (MARGIN + WIDTH) * player.x + MARGIN/2
    player_blit_y = (MARGIN + HEIGHT) * player.y + MARGIN/2
    game.gameDisplay.blit(player.player_sprites[player.sprite_idx], (player_blit_x, player_blit_y))

def load_q_table_from_file(agent):

    loaded_q_table = np.load("models.npy")

    print("loaded_q_table", loaded_q_table.shape)
    print("agent.q_table", agent.q_table.shape)

    assert loaded_q_table.shape == agent.q_table.shape, "shapes does not agree"

    agent.q_table = loaded_q_table

    print(loaded_q_table)

# event.type = MOUSEBUTTONDOWN
def ui_interaction(event, game):

    # User clicks the mouse. Get the position
    # Change the x/y screen coordinates to grid coordinates
    pos = pygame.mouse.get_pos()
    column = pos[0] // (WIDTH + MARGIN)
    row = pos[1] // (HEIGHT + MARGIN)

    game.add_enemy([row, column])

def handle_replay():

    while True:

        event = pygame.event.wait()

        if event.type == pygame.KEYDOWN:

            keys = pygame.key.get_pressed()

            if keys[pygame.K_r]:
                run()
            elif keys[pygame.K_q]:
                pygame.quit()

            break;

def run():

    pygame.init()
    agent = Agent()

    # possibly load q-table, possibly train ai
    if load_q_table == True:
        load_q_table_from_file(agent)

        if ai_mode == True and from_scratch == False:
            training_ai(agent)

    elif ai_mode == True: # or both load and train!
        # Train AI off screen
        training_ai(agent) # SEVERAL GAMES

    # After training, use agent to play the game
    agent.training = False

    # Initialize classes
    game = Game(WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE, True, num_enemies_game)
    enemies = game.enemies
    game.steps_required = 0
    game.lifes_gone = 0

    agent.init_agent(game)

    # Loop until the user clicks the close button.
    done = False

    # counter for enemy movement
    count_enemy = 0

    # for graphics
    special_playfield_tiles = []

    # ONE GAME
    while not done:

        # let player take step (ai mode)
        if ai_mode == True:
            ai_controller(game, agent)

            if ai_mode == False:
                pygame.time.wait(speed)

        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop

            # let player take step (user test mode)
            if event.type == pygame.KEYDOWN and ai_mode == False:
                # print(event.type)
                user_controller(event, game, agent)

            # add enemies on mouse click
            if event.type == pygame.MOUSEBUTTONDOWN:

                ui_interaction(event, game)

        game.player.closest_enemy_dist = INF_DIST

        # let enemies take a new step
        if ai_mode == True or count_enemy % 10 == 0: # Remember to move to AI as well
            for enemy in enemies:
                enemy.move(game)
        count_enemy += 1

        # Checking collisons
        game.player.check_collisions(game) # Remember to move to AI as well

        if game.env.filled_percentage >= game_won_percentage:

            done = True
            print("GAME WON")
            print(agent.q_table)
            print("steps_required", game.steps_required)

            q_sum_per_state = np.sum(agent.q_table, axis=1)
            #print("q_sum_per_state", q_sum_per_state )
            #print("q_sum_per_state shape", q_sum_per_state.shape )

            where = np.where(q_sum_per_state == 0)[0]

            print("where", where.shape[0], "of", q_sum_per_state.shape[0], "is zero"  ) # 767 av 1024 when training 150 games

            print_state_info(agent)

        draw_game(game)

        if ai_mode == True:
            pygame.time.wait(speed)

        # Limit to 60 frames per second, then update the screen
        game.clock.tick(60)
        pygame.display.flip() # alternative: pygame.display.update()
        game.steps_required += 1

    # save q_table to file
    if save_q_table == True:
        np.save("models", agent.q_table)

    if replay_mode == True:
        handle_replay() # press r to replay, q to quit
    else:
        pygame.quit()


run()
