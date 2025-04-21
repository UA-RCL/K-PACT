import os
import ast
import sys
import json
import csv
import copy
sys.path.append('.')
import common as common
import concurrent.futures

from greedy_clustering.placement import place
from utils import row_buffer_area_calculation, PE_array_area_calculation, IMEM_area_calculation

# Function to perform placement for a given IMEM size
def process_imem_size(IMEM_size, output_grids_path, output_locations_path, ds3_array_size=None, array_size=None, array_count=None):
    common.current_IMEM_size = IMEM_size

    # Read clustering data
    array_locs = {}
    array_sizes = []
    for array_id in range(array_count):
        with open(f"{common.redistributed_clusters_path}{int(IMEM_size / 8)}_lines_" + str(array_count) + "_arrays_id_" + str(array_id) + ".json", 'r') as json_file:
            bins = json.load(json_file)

        copy_bins = copy.deepcopy(bins)

        # Perform the placement for the given IMEM_size
        individual_array_locs, array_size = place(copy_bins, output_grids_path, array_id=array_id)
        array_locs[array_id] = individual_array_locs
        array_sizes.append(array_size)

        # Dumping the locations
        with open(f"{output_locations_path}/{int(IMEM_size/8)}_lines.json", 'w') as json_file:
            json.dump(array_locs, json_file, indent=1)
    
    final_number_of_PEs = None
    final_PE_array_area = None
    final_IMEM_area = None

    if isinstance(array_size, tuple):
        # Calculating the number of PEs
        final_number_of_PEs = 0
        for final_array_size in array_sizes:
            final_number_of_PEs += final_array_size[0] * final_array_size[1]
        # PE area given array size and number of arrays
        final_PE_array_area = PE_array_area_calculation(int(IMEM_size/8), final_number_of_PEs)
        # Buffer and crossbar area incorporation given row count and number of arrays
        final_PE_array_area += row_buffer_area_calculation(array_size[0]) * array_count
        # Converting to mm²
        final_PE_array_area /= 1000000
        final_IMEM_area = IMEM_area_calculation(int(IMEM_size/8), final_number_of_PEs)
    else:
        print("Hey, you messed something up real bad! Array size should be tuple\n")
        print("Exiting...")
        exit()
    return (IMEM_size, final_number_of_PEs, array_count, final_PE_array_area, final_IMEM_area, len(bins), final_array_size, array_sizes)

def array_sweep(array_size=None, array_count=None):

    # If ds3_integration is true, row and column count is swapped
    placement_base_path = common.placement_base_path + str(array_count) + "_arrays_" + str(common.initial_array_size) + "_initial_size"
    data_base_path = common.data_base_path + str(array_count) + "_arrays_" + str(common.initial_array_size) + "_initial_size"

    output_grids_path = placement_base_path + '/grids'
    if not os.path.exists(output_grids_path):
        os.makedirs(output_grids_path)

    output_locations_path = placement_base_path + '/locations'
    if not os.path.exists(placement_base_path + '/locations'):
        os.makedirs(placement_base_path + '/locations')
    csv_data = [("IMEM_Size", "Number_of_PEs", "Number of Arrays", "Array_Area", "IMEM_Area", "Cluster_Count", "Uniform Array Size", "Array Sizes")]

    with concurrent.futures.ProcessPoolExecutor(max_workers=common.number_of_workers) as executor:
        futures = {executor.submit(process_imem_size, IMEM_size, output_grids_path, output_locations_path, 
                                   array_count=array_count): IMEM_size for IMEM_size in common.IMEM_size_list}

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            csv_data.append(result)

    sorted_data = [csv_data[0]] + sorted(csv_data[1:], key=lambda x: x[0])

    if not os.path.exists(data_base_path):
        os.makedirs(data_base_path)

    with open(f"{data_base_path}/data.csv", mode="w", newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(sorted_data)