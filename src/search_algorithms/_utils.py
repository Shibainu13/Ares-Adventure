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


def find_positions(grid: list[list[str]], stone_weights: list[int]):
    """Find initial positions of Ares, stones, and switches

    Args:
        grid (list[list[str]]): initial map parsed from input.txt

    Returns:
        (tuple[int, int] | None, list[tuple[int, int]], list[tuple[int, int]]): Ares, stones and switches positions in (row, col)
    """
    ares_pos = None
    stones = []
    switches = []
    cnt = 0
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            if cell == '@' or cell == '+':
                ares_pos = (i, j)
            if cell == '$' or cell == '*':
                stones.append((i, j))
                grid[i][j] = str(stone_weights[cnt]) if cell == '$' else str(-stone_weights[cnt])
                cnt += 1
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
