import queue
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from constants import *

def BFS(queue, game, celltype):

    matrix = game.env.grid

    current_index = queue.get()
    current_x,current_y = current_index[0],current_index[1]

    element = matrix[current_y,current_x]

    if element == celltype: return [current_y,current_x]

    for n in range(current_x-1,current_x+2):
        for m in range(current_y-1,current_y+2):
            if not (n==current_x and m==current_y) \
                and n>-1 and m>-1 \
                and n<matrix.shape[0] and m<matrix.shape[1] \
                and (n,m) not in queue.queue :
                    queue.put((n,m))
    return BFS(queue, game, celltype)


def calculate_distance_to_cells(entity, cells, euclidian = False):
    # player = game.player
    min_dist = INF_DIST # from enemy to cell
    min_cell = cells[0]

    #print(cells)
    #print(cells.shape)
    # find which cell in risky lane is closest to this enemy
    for cell in cells:

        #print("min_dist", min_dist)
        # calculate manhattan distance
        if euclidian == True:

            distance = np.linalg.norm(np.asarray(entity.position)-np.asarray(cell))
        else:
            distance = abs(entity.y - cell[0]) + abs(entity.x - cell[1])
        #print("distance", distance)
        if distance < min_dist:
            min_dist = distance
            min_cell = cell

    return min_dist, min_cell


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

def plot_seaborn(array_counter, array_score, x_label, y_label):

    #print("array_counter", array_counter)
    #print("array_score", array_score)

    sns.set(color_codes=True)
    ax = sns.regplot(np.array([array_counter])[0], np.array([array_score])[0], color="b", x_jitter=.1, line_kws={'color':'green'})
    ax.set(xlabel=x_label, ylabel=y_label)
    plt.show()

def action_to_dirname(action):

    if action == [1, 0]:
        return "down"
    elif action == [0, 1]:
        return "right"
    elif action == [-1, 0]:
        return "up"
    elif action == [0, -1]:
        return "left"
    else:
        print("unvalid action")

# from a given pos, what's the minumum distance to a given celltype in one of the directions
def strict_direction_dist( game, pos, action, celltype ):

    grid = game.env.grid
    
    if grid[pos[0]][pos[1]] == celltype:
        return 0

    cell_dist = 1
    temp_pos = [pos[0] + action[0], pos[1] + action[1]]

    while game.env.within_grid(temp_pos) and grid[temp_pos[0]][temp_pos[1]] != celltype:

        cell_dist += 1
        temp_pos = [temp_pos[0] + action[0], temp_pos[1] + action[1]]

    return cell_dist


def get_new_enemy_dir(direction, enemy_pos, new_pos, game):

    new_dir = [-5,-5]

    if direction == [1,1]: # towards bottomright corner

        new_dir = [-1, 1]
        cell_to_right = [enemy_pos[0], enemy_pos[1] + 1 ]

        if game.env.grid[cell_to_right[0], cell_to_right[1] ] == BORDER:
            if cell_to_right == [new_pos[0] - 1, new_pos[1]]:
                new_dir = [1, -1]

    elif direction == [1,-1]: # towards bottomleft corner

        new_dir = [-1, -1]
        cell_to_left = [enemy_pos[0], enemy_pos[1] - 1 ]

        if game.env.grid[cell_to_left[0], cell_to_left[1] ] == BORDER:
            if cell_to_left == [new_pos[0] - 1, new_pos[1]]:
                new_dir = [1, 1]


    elif direction == [-1,1]: # towards topright corner

        new_dir = [1, 1]
        cell_to_right = [enemy_pos[0], enemy_pos[1] + 1 ]

        if game.env.grid[cell_to_right[0], cell_to_right[1] ] == BORDER:
            if cell_to_right == [new_pos[0] + 1, new_pos[1]]:
                new_dir = [-1, -1]


    elif direction == [-1,-1]: # towards topleft corner

        new_dir = [1, -1]
        cell_to_left = [enemy_pos[0], enemy_pos[1] - 1 ]
        cell_to_up = [enemy_pos[0] - 1, enemy_pos[1] ]

        # is left?
        if game.env.grid[cell_to_left[0], cell_to_left[1] ] == BORDER:
            if cell_to_left == [new_pos[0] + 1, new_pos[1]]:
                new_dir = [-1, 1]
        # # is top?
        # elif game.env.grid[cell_to_up[0], cell_to_up[1] ] == BORDER:
        #     if cell_to_up == [new_pos[0], new_pos[1] + 1]:
        #         new_dir = [1, -1]
        #     else:
        #         new_dir = [-1, -1]


    return new_dir

def print_state_info(agent):

    state_percents = agent.state_counter / agent.state_counter.sum()
    state_percents = np.around(state_percents, decimals=4)

    avg = np.average(state_percents)

    for i in range(agent.state_counter.shape[0]):
        if state_percents[i] > avg:
             print("state: ", i, ":", state_percents[i] ," %")
