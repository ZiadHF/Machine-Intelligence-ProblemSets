from typing import Any, Set, Tuple
from grid import Grid
import utils


def most_frequent_item(grid: Grid):
    '''
    This function finds the most frequently occurring value in a Grid.

    Returns:
      Any: the most repeated value in the grid.
           If multiple values have the same frequency, any one may be returned.
           If the grid is empty, return None.
    '''
    grid_dict = dict()
    for i in range(grid.width):
        for j in range(grid.height):
            value = grid[i, j]
            grid_dict[value] = grid_dict.get(value, 0) + 1
    max = None
    for key, count in grid_dict.items():
        if max is None or count > grid_dict[max]:
            max = key
    return max
