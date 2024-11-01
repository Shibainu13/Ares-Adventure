import os

# Define directions via row-col (e.g moving up = moving to the row above --> (row - 1, col))
DIRECTIONS = {
    'u': (-1, 0),
    'd': (1, 0),
    'l': (0, -1),
    'r': (0, 1)
}


def parse_input(input_string: str):
    """Define the Maze and Parse the Input

    Args:
        input_string (str): Raw input fetched from input.txt as string

    Returns:
        (list[int], list[list[str]]): a list of stone weights and map grid 
    """
    lines = input_string.strip().splitlines()
    stone_weights = list(map(int, lines[0].split()))
    grid = [list(line) for line in lines[1:]]
    return stone_weights, grid


def find_positions(grid: list[list[str]]):
    """Find initial positions of Ares, stones, and switches

    Args:
        grid (list[list[str]]): initial map parsed from input.txt

    Returns:
        (tuple[int, int] | None, list[tuple[int, int]], list[tuple[int, int]]): Ares, stones and switches positions in (row, col)
    """
    ares_pos = None
    stones = []
    switches = []
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            if cell == '@' or cell == '+':
                ares_pos = (i, j)
            if cell == '$' or cell == '*':
                stones.append((i, j))
            if cell == '.' or cell == '+' or cell == '*':
                switches.append((i, j))
    return ares_pos, stones, switches


def all_stones_on_switches(stones: list[tuple[int, int]], switches: list[tuple[int, int]]):
    """Check if all stones are on switches

    Args:
        stones (list[tuple[int, int]]): list of positions of stones
        switches (list[tuple[int, int]]): list of positions of switches

    Returns:
        bool: whether all stones are on switches
    """
    return all(stone in switches for stone in stones)

def heuristic_weighted_manhattan_distance(stones: list[tuple[int, int]], switches: list[tuple[int, int]], stone_weights: list[int]):
    """Calculate weighted Manhattan distance of stones to switches and the weight of the stones to estimate the remaining effort needed to complete the task of placing all stones on their designated switches

    Args:
        stones (list[tuple[int, int]]): list of positions of stones
        switches (list[tuple[int, int]]): list of positions of switches
        stone_weights (list[int]): list of stone weights

    Returns:
        int: heuristic value
    """
    total_weighted_distance = 0
    for i, st in enumerate(stones):
        # Find the closest switch for each stone using Mahattan distance
        min_distance = min(abs(st[0] - sw[0])+ abs(st[1] - sw[1]) for sw in switches)
        # Multiply the distance by the stone's weight
        total_weighted_distance += min_distance * stone_weights[i]
    return total_weighted_distance


def heuristic_manhattan_distance(stone, switch):
    """Calculate Manhattan distance of stones to switches to estimate the remaining effort needed to complete the task of placing all stones on their designated switches

    Args:
        stones (list[tuple[int, int]]): list of positions of stones
        switches (list[tuple[int, int]]): list of positions of switches

    Returns:
        int: heuristic value
    """
    return sum(min(abs(sx - sw[0]) + abs(sy - sw[1]) for sw in switch) for sx, sy in stone)

def listMaps():
    """List of all maps in the maps folder

    Returns:
        list[str]: list of all map names
    """
    list_Map=[]
    list_Map.append('Map1')
    list_Map.append('Map2')
    list_Map.append('Map3')
    list_Map.append('Map4')
    list_Map.append('Map5')
    return list_Map
