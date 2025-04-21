import ast
import math
import numpy as np
import matplotlib.pyplot as plt
import random
import common as common
import os

def place_kernel(kernel_name, kernel_shape, grid, grid_height=None, grid_width=None):
    """
    Places a kernel on a grid.

    Args:
        kernel_name (str): The name of the kernel to be placed.
        kernel_shape (tuple): A tuple (kernel_height, kernel_width) representing the shape of the kernel.
        grid (list of list): The grid on which the kernel is to be placed.
        grid_height (int, optional): The height of the grid.
        grid_width (int, optional): The width of the grid.

    Returns:
        tuple: Returns (row, col) where the kernel was placed.
    """
    kernel_height, kernel_width = kernel_shape

    # Very very bad way to handle this. Need to fix this.
    current_height = len(grid)
    for row in range(current_height):
        for col in range(grid_width):
            if can_place_kernel(row, col, kernel_shape, grid, current_height, grid_width):
                place_at(row, col, kernel_name, kernel_shape, grid)
                return row, col

    while len(grid) < current_height + kernel_height:
        grid.append([None] * grid_width)

    current_height = len(grid)
    for row in range(current_height):
        for col in range(grid_width):
            if can_place_kernel(row, col, kernel_shape, grid, current_height, grid_width):
                place_at(row, col, kernel_name, kernel_shape, grid)
                return row, col

    # place_at(current_height, 0, kernel_name, kernel_shape, grid)

    return current_height, 0

def can_place_kernel(row, col, kernel_shape, grid, grid_height, grid_width):
    """
    Determines if a kernel can be placed at a specified position in the grid.

    Args:
        row (int): The starting row index for placing the kernel.
        col (int): The starting column index for placing the kernel.
        kernel_shape (tuple): A tuple (kernel_height, kernel_width) representing the dimensions of the kernel.
        grid (list of list): A 2D list representing the grid where the kernel is to be placed.
        grid_height (int): The height of the grid.
        grid_width (int): The width of the grid.

    Returns:
        bool: True if the kernel can be placed at the specified position, False otherwise.
    """
    kernel_height, kernel_width = kernel_shape
    if row + kernel_height > grid_height or col + kernel_width > grid_width:
        return False
    return all(grid[r][c] is None for r in range(row, row + kernel_height) for c in range(col, col + kernel_width))

def place_at(row, col, kernel_name, kernel_shape, grid):
    """
    Places a kernel in a grid at the specified starting row and column.

    Args:
        row (int): The starting row index where the kernel will be placed.
        col (int): The starting column index where the kernel will be placed.
        kernel_name (str): The name of the kernel to place in the grid.
        kernel_shape (tuple): A tuple (height, width) representing the shape of the kernel.
        grid (list of list of str): The grid where the kernel will be placed.

    Returns:
        None
    """
    for r in range(row, row + kernel_shape[0]):
        for c in range(col, col + kernel_shape[1]):
            grid[r][c] = kernel_name

def visualize_placement(data, grid_size, array_id, grid_path, object_colors=None):
    """
    Visualizes the placement of objects on a grid and saves the visualization as a PDF.
    Parameters:
    data (list): A list of tuples or strings representing the coordinates and dimensions of objects.
                 Each tuple or string should contain (row, col, _, (height, width)).
    grid_size (tuple): A tuple representing the size of the grid (rows, cols).
    array_id (int): An identifier for the array.
    grid_path (str): The path where the grid visualization will be saved.
    object_colors (list, optional): A list of colors for the objects. If None, random colors will be generated.
    Returns:
    None
    """
    if object_colors is None:
        object_colors = [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in range(len(data))]

    data_3d = np.full((grid_size[0], grid_size[1], 3), 255, dtype=int)

    for i, coordinate in enumerate(data):
        if isinstance(coordinate, tuple):
            (row, col, _, (height, width)) = coordinate
        elif isinstance(coordinate, str):
            (row, col, _, (height, width)) = ast.literal_eval(coordinate)
            
        color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        for row_c in range(height):
            for col_c in range(width):
                data_3d[row + row_c][col + col_c] = color

    fig, ax = plt.subplots()
    ax.imshow(data_3d)

    ax.xaxis.set_tick_params(labelbottom=False)
    ax.yaxis.set_tick_params(labelleft=False)
    ax.set_xticks([])
    ax.set_yticks([])

    base_path = os.path.join(grid_path, f"IMEM_{int(common.current_IMEM_size / 8)}_lines")
    os.makedirs(base_path, exist_ok=True)

    plt.savefig(os.path.join(base_path, f"array_{array_id}.pdf"))
    plt.close()

def find_factors(k):
    return next((i, k // i) for i in range(int(math.sqrt(k)), 0, -1) if k % i == 0)

def place_to_array_given_count(bins, personality_dict, grid_path, array_id):
    grid_width = common.initial_array_size[0]
    grid = []

    array_locs = {}
    slices_to_append = {}
    for iter, (key, value) in enumerate(bins.items()):
        biggest_size = (0,0)
        biggest_pers1 = None
        biggest_pers2 = None
        for pers in value[0]:
            if personality_dict[pers][0][0] > biggest_size[0]:
                biggest_size = (personality_dict[pers][0][0], biggest_size[1])
                biggest_pers1 = pers
            if personality_dict[pers][0][1] > biggest_size[1]:
                biggest_size = (biggest_size[0], personality_dict[pers][0][1])
                biggest_pers2 = pers
        biggest_pers = biggest_pers1 + "-" + biggest_pers2

        row_id, col_id = place_kernel(biggest_pers, biggest_size, grid, grid_width=grid_width)
        array_locs[key] = (row_id, col_id, value[2], biggest_size)
        slices_to_append[key] = value[1]

    grid = [row for row in grid if not all(cell is None for cell in row)]
    final_array_locs = {}
    for key, value in array_locs.items():
        coordinate = (value[0], value[1], value[2], value[3])
        final_array_locs[str(coordinate)] = []
        for pers in bins[key][0]:
            final_array_locs[str(coordinate)].append([pers, personality_dict[pers][0], int(personality_dict[pers][1]/8)])

    array_size = (len(grid), len(grid[0]))

    visualize_placement(list(final_array_locs.keys()), array_size, array_id, grid_path)

    if len(bins) != len(final_array_locs.keys()):
        print("Some bins are missing after placement!! Exiting ...")
        exit()

    return final_array_locs, array_size

def place(bins, grid_path, array_size=None, array_id=None):
    """
    Places items into bins based on their sizes and personalities, and sorts them according to specific criteria.
    Args:
        bins (dict): A dictionary where keys are bin identifiers and values are lists of personalities.
        grid_path (str): The path to the grid file.
        array_size (tuple, optional): The size of the array to place items into. Defaults to None.
        array_id (int, optional): The identifier for the array. Defaults to None.
    Returns:
        tuple: A tuple containing:
            - array_locs (dict): A dictionary with the locations of the arrays.
            - number_of_arrays (int or tuple): The number of arrays or the size of the array depending on the tool mode.
    """
    bin_sizes_and_bins = {}
    for iter, (key, value) in enumerate(bins.items()):
        biggest_size = (0,0)
        biggest_pers1 = None
        biggest_pers2 = None
        for pers in value[0]:
            if common.personality_dict[pers][0][0] > biggest_size[0]: # or personality_dict[pers][0][1] > biggest_size[1]:
                biggest_size = (common.personality_dict[pers][0][0], biggest_size[1])
                biggest_pers1 = pers
            if common.personality_dict[pers][0][1] > biggest_size[1]: # or personality_dict[pers][0][1] > biggest_size[1]:
                biggest_size = (biggest_size[0], common.personality_dict[pers][0][1])
                biggest_pers2 = pers
        biggest_pers = biggest_pers1 + "-" + biggest_pers2
        n_PEs = biggest_size[0] * biggest_size[1]
        if n_PEs not in bin_sizes_and_bins:
            bin_sizes_and_bins[n_PEs] = []
            bin_sizes_and_bins[n_PEs].append((key,value))
        else:
            bin_sizes_and_bins[n_PEs].append((key,value))
    
    sorted_dict = {k: sorted([v], reverse=True)[0] for k, v in sorted(bin_sizes_and_bins.items(), key=lambda item: item[0], reverse=True)}
    sorted_bins = {}

    if common.ED_kurtosis_mode:
        for (key,value) in sorted_dict.items():
            for idx, item in enumerate(value):
                if item[1][0] == ['energy_detect1_0', 'Kurtosis_0']:
                    sorted_bins[item[0]] = item[1]
                elif item[1][0] == ['energy_detect1_0']:
                    sorted_bins[item[0]] = item[1]
                elif item[1][0] == ['Kurtosis_0']:
                    sorted_bins[item[0]] = item[1]
                # elif item[1][0] == ['ED8_atn_0']:
                #     sorted_bins[item[0]] = item[1]
                else:
                    continue
    for (key,value) in sorted_dict.items():
        for item in value:
            if common.ED_kurtosis_mode:
                if item[1][0] == ['energy_detect1_0', 'Kurtosis_0']:
                    continue
                elif item[1][0] == ['energy_detect1_0']:
                    continue
                elif item[1][0] == ['Kurtosis_0']:
                    continue
                # elif item[1][0] == ['ED8_atn_0']:
                #     continue
            sorted_bins[item[0]] = item[1]
    
    
    array_locs, array_size = place_to_array_given_count(sorted_bins, common.personality_dict, grid_path, array_id)
    return array_locs, (array_size[1],array_size[0])

