import queue

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
