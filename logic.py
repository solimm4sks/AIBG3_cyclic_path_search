move_map = {0 : 'w', 1 : 'e', 2 : 'd', 3 : 's', 4 : 'a', 5 : 'q'}

def bounded_index(x, y, BOARD_X, BOARD_Y):
    return (0 <= x < BOARD_X and 0 <= y < BOARD_Y)

def valid_tile(x, y, BOARD_X, BOARD_Y, enemy_y, enemy_x, world_map):
    blockingTiles = ["POND", "HOLE"]
    retVal = bounded_index(x, y, BOARD_X, BOARD_Y)
    #if retVal:
        #print(x, y, world_map[x][y].itemType, bounded_index(x, y, BOARD_X, BOARD_Y), end='')
    retVal = retVal and world_map[x][y].itemType not in blockingTiles and not (x == enemy_x and y == enemy_y)
    #print(retVal)

    return retVal

# [6] -> [] -> (x, y, dist, nectar)
def get_reachable(_x, _y, world_map, BOARD_X, BOARD_Y, enemy_x, enemy_y, visited):
    flower = ["CHERRY_BLOSSOM", "LILAC", "ROSE", "SUNFLOWER"]
    parity = (_x % 2)
    adj = [[[-2, 0], [-1, 0], [+1, 0], [+2, 0], [+1, -1], [-1, -1]],
            [[-2, 0], [-1, 1], [1, 1], [2, 0], [1, 0], [-1, 0]]]
    reach_dir = [[] for i in range(6)]
    for i in range(6):
        next_pos = [_x, _y]
        parity = (_x % 2)
        next_pos[0] += adj[parity][i][0]
        next_pos[1] += adj[parity][i][1]
        parity = next_pos[0] % 2
        dist = 1
        nec = 0
        if bounded_index(next_pos[0], next_pos[1], BOARD_X, BOARD_Y) and not visited[next_pos[0]][next_pos[1]] and world_map[next_pos[0]][next_pos[1]].itemType in flower:
            nec += world_map[next_pos[0]][next_pos[1]].numOfItems
        while valid_tile(next_pos[0], next_pos[1], BOARD_X, BOARD_Y, enemy_x, enemy_y, world_map):
            reach_dir[i].append((next_pos[0], next_pos[1], dist, nec))
            next_pos[0] += adj[parity][i][0]
            next_pos[1] += adj[parity][i][1]
            parity = next_pos[0] % 2
            dist += 1
            if bounded_index(next_pos[0], next_pos[1], BOARD_X, BOARD_Y) and not visited[next_pos[0]][next_pos[1]] and world_map[next_pos[0]][next_pos[1]].itemType in flower:
                nec += world_map[next_pos[0]][next_pos[1]].numOfItems
    return reach_dir

def best_line(start_x, start_y, energy, nectar, world_map, BOARD_X, BOARD_Y, enemy_x, enemy_y):
    position_queue = [] # (x, y, nectar, energy, last_direction)
    move_queue = []
    current_position = [0, 0]
    current_position[0] = start_x
    current_position[1] = start_y
    c_energy = energy
    c_nectar = nectar
    position_queue.append((current_position[0], current_position[1], c_nectar, c_energy, -1))
    visited = [[False for x in range(BOARD_Y)] for x in range(BOARD_X)]

    best_nectar = -1
    best_moves = []

    while len(position_queue) != 0:
        (cp_x, cp_y, c_nectar, c_energy, ld) = position_queue.pop(0)
        moves = []
        if len(move_queue) != 0:
            moves = move_queue.pop(0)

        visited[cp_x][cp_y] = True
        # print(cp_x, cp_y, c_nectar, c_energy, ld, moves)
        if c_nectar == 100:
            return (moves, 100)
        
        if c_nectar > best_nectar:
            best_nectar = c_nectar
            best_moves = moves.copy()

        reachables = get_reachable(cp_x, cp_y, world_map, BOARD_X, BOARD_Y, enemy_x, enemy_y, visited)
        mx_dist = max([len(x) for x in reachables])
        for dst in range(mx_dist):
            for i in range(6):
                if i == ld:
                    continue
                if dst >= len(reachables[i]):
                    continue
                (x, y, dist, nec) = reachables[i][dst]
                if visited[x][y]:
                    continue

                new_moves = moves.copy()
                new_nectar = min(c_nectar + nec, 100)
                new_energy = c_energy
                new_energy -= dist * 2
                while new_energy <= 0:
                    new_moves.append({"type":"skip"})
                    new_energy += 5
                new_moves.append({"type": "move", "distance": dist, "direction": move_map[i]})
                
                move_queue.append(new_moves)
                position_queue.append((x, y, new_nectar, new_energy, i))

    return (best_moves, best_nectar)

def shortest_path_to_base(start_x, start_y, energy, nectar, world_map, BOARD_X, BOARD_Y, HIVE_X, HIVE_Y, enemy_x, enemy_y):
    position_queue = [] # (x, y, nectar, energy, last_direction)
    move_queue = []
    current_position = [0, 0]
    current_position[0] = start_x
    current_position[1] = start_y
    c_energy = energy
    c_nectar = nectar
    position_queue.append((current_position[0], current_position[1], c_nectar, c_energy, -1))
    visited = [[False for x in range(BOARD_Y)] for x in range(BOARD_X)]

    while len(position_queue) != 0:
        (cp_x, cp_y, c_nectar, c_energy, ld) = position_queue.pop(0)
        moves = []
        if len(move_queue) != 0:
            moves = move_queue.pop(0)

        visited[cp_x][cp_y] = True
        # print(cp_x, cp_y, c_nectar, c_energy, ld, moves)
        if cp_x == HIVE_X and cp_y == HIVE_Y:
            return moves


        reachables = get_reachable(cp_x, cp_y, world_map, BOARD_X, BOARD_Y, enemy_x, enemy_y, visited)
        mx_dist = max([len(x) for x in reachables])
        for dst in range(mx_dist):
            for i in range(6):
                if i == ld:
                    continue
                if dst >= len(reachables[i]):
                    continue
                (x, y, dist, nec) = reachables[i][dst]
                if visited[x][y]:
                    continue

                new_moves = moves.copy()
                new_nectar = min(c_nectar + nec, 100)
                new_energy = c_energy
                new_energy -= dist * 2
                while new_energy <= 0:
                    new_moves.append({"type":"skip"})
                    new_energy += 5
                new_moves.append({"type": "move", "distance": dist, "direction": move_map[i]})
                
                move_queue.append(new_moves)
                position_queue.append((x, y, new_nectar, new_energy, i))

    return -1