import os
import heapq
import time
import tracemalloc
from utils import parse_input, find_positions, all_stones_on_switches, heuristic_weighted_manhattan_distance, DIRECTIONS


def gbfs(grid, ares_pos, stones, switches, stone_weights):
    tracemalloc.start()
    start_time = time.time()
    
    queue = []
    heapq.heappush(queue, (0, ares_pos, stones, '', 0))
    visited = set()
    nodes_generated = 0
    
    while queue:
        h_cost, (ares_x, ares_y), stones, path, total_cost = heapq.heappop(queue)
        nodes_generated += 1
        
        if all_stones_on_switches(stones, switches):
            end_time = time.time()
            _, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            return {
                'steps': len(path),
                'weight': total_cost,
                'nodes': nodes_generated,
                'time_ms': "{:.2f}".format(1000 * (end_time - start_time)),
                'memory_mb': "{:.2f}".format(peak_memory / (1024 * 1024)),
                'path': path,
            }
        
        visited.add((ares_x, ares_y, tuple(stones)))
        
        for move, (dx, dy) in DIRECTIONS.items():
            new_x, new_y = ares_x + dx, ares_y + dy
            
            if grid[new_x][new_y] == '#':
                continue
            
            new_stones = stones[:]
            move_cost = 1
            
            if (new_x, new_y) in stones:
                stone_idx = stones.index((new_x, new_y))
                stone_x, stone_y = new_x + dx, new_y + dy
                
                if grid[stone_x][stone_y] == '#' or (stone_x, stone_y) in stones:
                    continue
                
                new_stones[stone_idx] = (stone_x, stone_y)
                move_cost += stone_weights[stone_idx]
                
                move = move.upper()
                
            new_total_cost = total_cost + move_cost
            new_heuristic = heuristic_weighted_manhattan_distance(new_stones, switches, stone_weights)
            
            new_state = (new_x, new_y, tuple(new_stones))
            if new_state not in visited:
                heapq.heappush(queue, (new_heuristic, (new_x, new_y), new_stones, path + move, new_total_cost))
                
    return None



# The code below is for testing only!!!

input_file_path = os.path.join('..', '..', 'maps', 'sample-input.txt')

def main():
    with open(input_file_path, 'r') as f:
        input_string = f.read()
        
    stone_weights, grid = parse_input(input_string)
    ares_pos, stones, switches = find_positions(grid)
    
    start_time = time.time()
    result = gbfs(grid, ares_pos, stones, switches, stone_weights)
    end_time = time.time()
    
    if result:
        print(result)
    else:
        print('GBFS: No solution found.')
        
if __name__ == "__main__":
    main()