from . import _utils
import os
import tracemalloc
import time
import heapq

def ucs(grid, ares_pos, stones, switches, stone_weights):
    tracemalloc.start()
    start_time = time.time()

    priority_queue = [(0, ares_pos, stones, '')]

    visited = {}

    while priority_queue:
        total_cost, (ares_x, ares_y), stones, path = heapq.heappop(priority_queue)

        if _utils.all_stones_on_switches(stones, switches):
            end_time = time.time()
            _, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            return {
                'steps': len(path),
                'weight': total_cost,
                'time_ms': "{:.2f}".format(1000 * (end_time - start_time)),
                'memory_mb': "{:.2f}".format(peak_memory / 1048576),
                'path': path,
            }

        if (ares_x, ares_y, tuple(stones)) in visited:
            continue

        visited[(ares_x, ares_y, tuple(stones))] = total_cost

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

            heapq.heappush(priority_queue, (new_total_cost, (new_x, new_y), new_stones, path + move))
    end_time = time.time()
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        'steps': None,
        'weight': None,
        'time_ms': "{:.2f}".format(1000 * (end_time - start_time)),
        'memory_mb': "{:.2f}".format(peak_memory / 1048576),
        'path': None,
    }


input_file = os.path.join('..', '..', 'maps', 'sample-input.txt')

def main(input_file=input_file):
    with open(input_file, 'r') as file:
        input_string = file.read()
    
    stone_weights, grid = _utils.parse_input(input_string)
    ares_pos, stones, switches = _utils.find_positions(grid)
    result = ucs(grid, ares_pos, stones, switches, stone_weights)
    if result:
        print(result)
    else:
        print('No solution found')

if __name__ == '__main__':
    main()