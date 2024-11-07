import os
import time
import tracemalloc
from . import _utils

def bfs(grid, ares_pos, stones, switches, stone_weights):
    tracemalloc.start()
    start_time = time.time()

    queue = [(ares_pos, stones, '', 0, [])]
    
    visited = dict()
    visited[(ares_pos[0], ares_pos[1], tuple(stones))] = 0
    nodes_generated = 0
    while queue:
        (ares_x, ares_y), stones, path, total_cost, weight_track = queue.pop(0)

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
                'weight_track': weight_track
            }
      

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

            if new_state not in visited or new_total_cost < visited[new_state]:
                visited[new_state] = new_total_cost
                queue.append(((new_x, new_y), new_stones, path + move, new_total_cost, weight_track + [new_total_cost]))
                nodes_generated += 1

    return None
