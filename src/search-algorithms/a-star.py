import time
import heapq
import tracemalloc
from _utils import all_stones_on_switches, parse_input, find_positions, DIRECTIONS

def a_star(grid, ares, stones, stone_weights, switches):
    start_time = time.time()
    tracemalloc.start()
    
    frontier = []
    reached = {}
    node_generated = 0

    init_h = heuristic_weighted_manhattan_distance(ares, stones, switches, stone_weights)
    heapq.heappush(frontier, (init_h, (0, ares, stones, '')))
    
    while frontier:
        f_current, node_current = heapq.heappop(frontier)
        g_current, ares, stones, path = node_current
        node_generated += 1
        
        if all_stones_on_switches(stones, switches):
            end_time = time.time()
            _, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            return {
                'steps': len(path),
                'weight': g_current,
                'nodes:': node_generated,
                'time_ms': "{:.2f}".format(1000 * (end_time - start_time)),
                'memory_mb': "{:.2f}".format(peak_memory / 1048576),
                'path': path
            }

        neighbors = generate_neighbors(grid, ares, stones, stone_weights)
        for move, new_ares, new_stones, move_cost in neighbors:
            tentative_g = g_current + move_cost
            new_state = (new_ares, new_stones)
            
            if new_state not in reached or tentative_g < reached[new_state][0]:
                h_successor = heuristic_weighted_manhattan_distance(new_ares, new_stones, switches, stone_weights)
                node_successor = (tentative_g, new_ares, new_stones, path + move)
                reached[(new_ares, new_stones)] = node_successor
                heapq.heappush(frontier, (tentative_g + h_successor, node_successor))
                        
    return None


def generate_neighbors(grid, ares, stones, stone_weights):
    neighbors = []
    ares_x, ares_y = ares
    
    for move, (dx, dy) in DIRECTIONS.items():
        new_x, new_y = ares_x + dx, ares_y + dy
        
        if grid[new_x][new_y] == '#':
            continue
        
        new_stones = list(stones)
        move_cost = 1
        
        if (new_x, new_y) in stones:
            stone_idx = stones.index((new_x, new_y))
            stone_x, stone_y = new_x + dx, new_y + dy
            
            if grid[stone_x][stone_y] == '#' or (stone_x, stone_y) in stones:
                continue
            
            new_stones[stone_idx] = (stone_x, stone_y)
            move_cost += stone_weights[stone_idx]
            move = move.upper()
            
        neighbors.append((move, (new_x, new_y), tuple(new_stones), move_cost))
        
    return neighbors 


def heuristic_weighted_manhattan_distance(ares_pos, stones, switches, stone_weights):
    total_heuristic = 0
    
    for i, stone in enumerate(stones):
        # Calculate the Manhattan distance from Ares to the current stone
        ares_to_stone_dist = abs(ares_pos[0] - stone[0]) + abs(ares_pos[1] - stone[1])
        
        # Find the minimum weighted Manhattan distance from the stone to any switch
        stone_to_switch_dist = min(
            abs(stone[0] - switch[0]) + abs(stone[1] - switch[1]) for switch in switches
        )
        
        # Compute the heuristic component for this stone
        heuristic_value = ares_to_stone_dist / 2 + stone_to_switch_dist * (stone_weights[i] + 1)
        total_heuristic += heuristic_value
    
    return total_heuristic


def main():
    filename = '../../maps/input3.txt'
    with open(filename, 'r') as f:
        input_string = f.read()
        
    stone_weights, grid = parse_input(input_string)
    ares_position, stone_positions, switch_positions = find_positions(grid)
    
    result = a_star(grid, ares_position, stone_positions, stone_weights, switch_positions)
    
    if result:
        print(result)
    else:
        print('No solution found!')
        

if __name__ == '__main__':
    main()