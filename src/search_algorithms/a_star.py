import time
import heapq
import tracemalloc
from . import _utils
# import _utils

def a_star(grid, ares, stones, stone_weights, switches):
    start_time = time.time()
    tracemalloc.start()
    
    frontier = []
    reached = {}
    node_generated = 0

    init_h = heuristic_weighted_manhattan_distance(ares, stones, switches, stone_weights)
    heapq.heappush(frontier, (init_h, (0, ares, stones, '', 0, []))) # f, ares, stones, path, total cost, weight track
    
    while frontier:
        _, node_current = heapq.heappop(frontier)
        g_current, ares, stones, path, total_cost, weight_track = node_current
        node_generated += 1
        
        if _utils.all_stones_on_switches(stones, switches):
            end_time = time.time()
            _, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            return {
                'steps': len(path),
                'weight': total_cost,
                'nodes:': node_generated,
                'time_ms': "{:.2f}".format(1000 * (end_time - start_time)),
                'memory_mb': "{:.2f}".format(peak_memory / 1048576),
                'path': path,
                'weight_track': weight_track
            }

        neighbors = generate_neighbors(grid, ares, stones, stone_weights, switches)
        for move, new_ares, new_stones, cost in neighbors:
            tentative_g = g_current + 1
            new_state = (new_ares, new_stones)
            
            if new_state not in reached or tentative_g < reached[new_state][0]:
                h_successor = heuristic_weighted_manhattan_distance(new_ares, new_stones, switches, stone_weights)
                node_successor = (tentative_g, new_ares, new_stones, path + move, total_cost + cost, weight_track + [total_cost + cost])
                reached[(new_ares, new_stones)] = node_successor
                heapq.heappush(frontier, (tentative_g + h_successor, node_successor))
                        
    return None


def generate_neighbors(grid, ares, stones, stone_weights, switches):
    neighbors = []
    ares_x, ares_y = ares
    
    for move, (dx, dy) in _utils.DIRECTIONS.items():
        new_x, new_y = ares_x + dx, ares_y + dy
        
        if grid[new_x][new_y] == '#':
            continue
        
        move_cost = 1
        new_stones = list(stones)
        
        if (new_x, new_y) in stones:
            stone_idx = stones.index((new_x, new_y))
            stone_x, stone_y = new_x + dx, new_y + dy
            
            if grid[stone_x][stone_y] == '#' or (stone_x, stone_y) in stones:
                continue
            
            new_stones[stone_idx] = (stone_x, stone_y)
            if corner_deadlock(grid, (stone_x, stone_y), new_stones, switches):
                continue
            
            move = move.upper()
            move_cost += stone_weights[stone_idx]
            
        neighbors.append((move, (new_x, new_y), tuple(new_stones), move_cost))
        
    return neighbors 


def heuristic_weighted_manhattan_distance(ares_pos, stones, switches, stone_weights):
    total_heuristic = 0
    min_ares_to_stone_dist = -1
    
    for i, stone in enumerate(stones):
        # Calculate the Manhattan distance from Ares to the current stone
        ares_to_stone_dist = abs(ares_pos[0] - stone[0]) + abs(ares_pos[1] - stone[1])
        if min_ares_to_stone_dist == -1 or ares_to_stone_dist < min_ares_to_stone_dist:
            min_ares_to_stone_dist = ares_to_stone_dist
        
        # Find the minimum weighted Manhattan distance from the stone to any switch
        stone_to_switch_dist = min(
            abs(stone[0] - switch[0]) + abs(stone[1] - switch[1]) for switch in switches
        )
        
        # Compute the heuristic component for this stone
        total_heuristic += stone_to_switch_dist * (stone_weights[i] + 1)
    
    return total_heuristic + min_ares_to_stone_dist


def corner_deadlock(grid, stone, stones, switches):
    stone_x, stone_y = stone
    
    on_switch = (stone_x, stone_y) in switches
    up_block = grid[stone_x][stone_y - 1] == '#' or ((stone_x, stone_y - 1) in stones and (stone_x, stone_y - 1) not in switches)
    down_block = grid[stone_x][stone_y + 1] == '#' or ((stone_x, stone_y + 1) in stones and (stone_x, stone_y + 1) not in switches)
    left_block = grid[stone_x - 1][stone_y] == '#' or ((stone_x - 1, stone_y) in stones and (stone_x - 1, stone_y) not in switches)
    right_block = grid[stone_x + 1][stone_y] == '#' or ((stone_x + 1, stone_y) in stones and (stone_x + 1, stone_y) not in switches)
    
    return (up_block or down_block) and (left_block or right_block) and not on_switch


def main():
    filename = '../../maps/input1.txt'
    with open(filename, 'r') as f:
        input_string = f.read()
        
    stone_weights, grid = _utils.parse_input(input_string)
    ares_position, stone_positions, switch_positions = _utils.find_positions(grid)
    
    result = a_star(grid, ares_position, stone_positions, stone_weights, switch_positions)
    
    if result:
        print(result)
    else:
        print('No solution found!')
        

if __name__ == '__main__':
    main()