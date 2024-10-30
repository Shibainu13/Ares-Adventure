import time
import heapq
import tracemalloc
from _utils import all_stones_on_switches, parse_input, find_positions, DIRECTIONS

def a_star(grid, ares_position, stone_positions, stone_weights, switch_positions):
    start_time = time.time()
    tracemalloc.start()
    
    open_list = []
    closed_list = []
    parent_map = {}
    
    node_start = (ares_position, tuple(stone_positions))
    node_visited = 0
    g_score = {node_start: 0}
    h_score = heuristic_weighted_manhattan_distance(ares_position, stone_positions, switch_positions, stone_weights)
    f_score = {node_start: h_score}
    heapq.heappush(open_list, (h_score, node_start))
    
    while open_list:
        f_current, node_current = heapq.heappop(open_list)
        ares, stones = node_current
        node_visited += 1
        
        if all_stones_on_switches(stones, switch_positions):
            end_time = time.time()
            _, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            path = reconstruct_path(parent_map, node_current)
            
            return {
                'steps': len(path),
                'weight': g_score[node_current],
                'nodes:': node_visited,
                'time_ms': "{:.2f}".format(1000 * (end_time - start_time)),
                'memory_mb': "{:.2f}".format(peak_memory / 1048576),
                'path': path
            }
        
        for move, new_ares, new_stones, move_cost in generate_neighbors(grid, ares, stones, stone_weights):
            node_successor = (new_ares, new_stones)
            successor_current_cost = g_score[node_current] + move_cost
            
            if node_successor in g_score and g_score[node_successor] <= successor_current_cost:
                continue  # Skip if we've already found a cheaper path to this node
            
            if node_successor not in closed_list:
                if node_successor not in [n[1] for n in open_list]:
                    # Heuristic for the successor to the goal
                    h_successor = heuristic_weighted_manhattan_distance(new_ares, new_stones, switch_positions, stone_weights)
                    f_score[node_successor] = successor_current_cost + h_successor
                    heapq.heappush(open_list, (f_score[node_successor], node_successor))
                
                # Update scores and parent information
                g_score[node_successor] = successor_current_cost
                parent_map[node_successor] = (node_current, move)
            elif g_score[node_successor] > successor_current_cost:
                # If the node is in CLOSED with a higher cost, update and move it to OPEN
                closed_list.remove(node_successor)
                heapq.heappush(open_list, (f_score[node_successor], node_successor))

        closed_list.append(node_current)
    
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


def reconstruct_path(parent_map, node):
    path = []
    while node in parent_map:
        node, move = parent_map[node]
        path.append(move)
    return ''.join(path[::-1])   


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
    filename = '../../maps/sample-input.txt'
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