import _utils
import os
import time
import tracemalloc

def dfs(grid, ares_pos, stones, switches, stone_weights):
    tracemalloc.start()
    start_time = time.time()

    stack = [(ares_pos, stones, '', 0)]
    visited = set()
    nodes_generated = 0

    while stack:
        (ares_x, ares_y), stones, path, total_cost = stack.pop()
        nodes_generated += 1

        if _utils.all_stones_on_switches(stones, switches):
            end_time = time.time()
            _, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            return {
                'steps': len(path),
                'weight': total_cost,
                'nodes': nodes_generated,
                'time_ms': "{:.2f}".format(1000 * (end_time - start_time)),
                'memory_mb': "{:.2f}".format(peak_memory / 1048576),
                'path': path,
            }
        
        visited.add((ares_x, ares_y, tuple(stones)))

        for move, (dx, dy) in _utils.DIRECTIONS.items():
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
            new_state = (new_x, new_y, tuple(new_stones))

            if new_state not in visited:
                stack.append(((new_x, new_y), new_stones, path + move, new_total_cost))

    return None

input_file = os.path.join('..', '..', 'maps', 'sample-input.txt')

def main(input_file=input_file):
    print(input_file)
    with open(input_file, 'r') as file:
        input_string = file.read()
    
    stone_weights, grid = _utils.parse_input(input_string)
    ares_pos, stones, switches = _utils.find_positions(grid)
    result = dfs(grid, ares_pos, stones, switches, stone_weights)

    if result is not None:
        print(result)
    else:
        print('DFS: No solution found')

if __name__ == '__main__':
    main()
