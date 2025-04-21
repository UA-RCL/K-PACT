import sys
sys.path.append(".")

import ast
import argparse
import common
import time
import copy
import os
from utils import calculate_IMEM_sizes, preprocess
from scripts.clustering_sweep import IMEM_sweep
from scripts.placement_sweep import array_sweep

def parse_args():
    parser = argparse.ArgumentParser(description="Clustering and placement input configuration.")

    parser.add_argument('--array_count', type=str, default="(4,4)", help='number of arrays for placement')
    parser.add_argument('--initial_array_size', type=str, default="(32,32)", help='array size with which timing info is collected')
    parser.add_argument('--number_of_IMEM_sizes', type=int, default=32, help='desired number of IMEM sizes to sweep')
    parser.add_argument('--number_of_trees', type=int, default=15, help='number of unique trees')
    parser.add_argument('--number_of_subbands', type=int, default=48, help='number of active subbands')

    parser.add_argument('--heterogeneity_type', type=int, default=1, help='heterogeneous clustering:0, homogeneous clustering:1')
    parser.add_argument('--ED_kurtosis_mode', type=int, default=1, help='ED-kurtosis clustering mode')
    parser.add_argument('--parallelization', type=int, default=0, help='0: parallelization disabled, 1:parallelization enabled')
    parser.add_argument('--number_of_workers', type=int, default=1, help='number of threads if parallelization is enabled')
    parser.add_argument('--output_dir', type=str, default="output", help='Directory to store output files')

    args = parser.parse_args()
    return args

def run():

    start_time = time.time()
    config_names = []

    for array_count in range(common.array_count[0], common.array_count[1] + 1):        
        file_path = "input_data.json"
        common.personality_dict = preprocess(file_path, array_count)
        
        temp_timing_data = copy.deepcopy(common.timing_data.data)            

        for array_id in range(array_count):
            common.timing_data.data = temp_timing_data[array_id]
            common.ED_kurtosis_mode = args.ED_kurtosis_mode
            IMEM_sweep(array_id, array_count)

        common.ED_kurtosis_mode = args.ED_kurtosis_mode

        # Define configuration name
        config_name = f"{array_count}_arrays_{common.initial_array_size}_initial_size"
        config_names.append(config_name)            
        array_sweep(array_count=array_count)

    end_time = time.time()
    print("Elapsed time for clustering and placement:", end_time - start_time, "seconds")

if __name__ == "__main__":
    args = parse_args()

    common.array_count = ast.literal_eval(args.array_count)
    common.homogeneous = args.heterogeneity_type
    common.number_of_IMEM_sizes = args.number_of_IMEM_sizes
    common.number_of_trees = args.number_of_trees
    common.subband_count = args.number_of_subbands
    common.initial_array_size = ast.literal_eval(args.initial_array_size)
    common.ED_kurtosis_mode = args.ED_kurtosis_mode
    common.output_dir = args.output_dir
    common.base_path = args.output_dir + "/"

    if common.parallelization:
        common.number_of_workers = args.number_of_workers
    else:
        common.number_of_workers = 1

    common.IMEM_size_list, common.IMEM_size_list_lines, common.IMEM_size_list_KB = calculate_IMEM_sizes()

    if not os.path.exists(common.base_path):
        os.makedirs(common.base_path)

    common.base_path += f"{common.array_count}_arrays_{common.initial_array_size}_initial_size/"

    found = False
    biggest_id = 0
    for folder_name in os.listdir(common.output_dir):
        if os.path.isdir(f"{common.output_dir}{folder_name}") and common.base_path[7:] in folder_name:
            found = True
            if int(folder_name.split("_")[-1]) > biggest_id:
                biggest_id = int(folder_name.split("_")[-1])

    if not found:
        common.base_path += str(0)  
    else:
        common.base_path += str(biggest_id + 1)

    if not os.path.exists(common.base_path):
        os.makedirs(common.base_path)

    f = open(common.base_path + "/env_conf.txt", "w")

    print("Array count:", common.array_count)
    f.write("Array count: " + str(common.array_count) + "\n")

    print("Timing information collection performed with an array of size:", common.initial_array_size)
    f.write("Timing information collection performed with an array of size: " + str(common.initial_array_size) + "\n")

    print("Number of unique trees:", common.number_of_trees)
    f.write("Number of unique trees: " + str(common.number_of_trees) + "\n")
    
    print("Number of active subbands:", common.subband_count)
    f.write("Number of active subbands: " + str(common.subband_count) + "\n")

    print("Sweeping", common.number_of_IMEM_sizes, "IMEM lines")
    f.write("Sweeping " + str(common.number_of_IMEM_sizes) + " IMEM lines" + "\n")

    print("Homogeneity type:", "Homogeneous" if common.homogeneous else "Heterogeneous")
    f.write("Homogeneity type: ")
    f.write("Homogeneous\n" if common.homogeneous else "Heterogeneous" + "\n")

    print("ED+Kurtosis clustering mode:", "Enabled" if common.ED_kurtosis_mode else "Disabled")
    f.write("ED+Kurtosis clustering mode: ")
    f.write("Enabled\n" if common.ED_kurtosis_mode else "Disabled" + "\n")

    print("Parallelization:", "Enabled" if common.parallelization else "Disabled")
    f.write("Parallelization: ")
    f.write("Enabled\n" if common.parallelization else "Disabled" + "\n")

    print("Number of workers:", common.number_of_workers)
    f.write("Number of workers:" + str(common.number_of_workers)  + "\n")

    print("Output directory:", common.output_dir)
    f.write("Output directory:" + str(common.output_dir)  + "\n")
    f.close()

    common.clustering_base_path = common.base_path + '/clustering/'
    common.redistributed_clusters_path = common.clustering_base_path + '/redistributed_clusters/'
    common.unlimited_clusters_path = common.clustering_base_path + '/unlimited_clusters/'
    common.placement_base_path = common.base_path + '/placement/'
    common.data_base_path = common.base_path + '/data/'

    if not os.path.exists(common.clustering_base_path):
        os.makedirs(common.clustering_base_path)
    if not os.path.exists(common.clustering_base_path + 'redistributed_clusters/'):
        os.makedirs(common.clustering_base_path + 'redistributed_clusters/')
    if not os.path.exists(common.clustering_base_path + 'unlimited_clusters/'):
        os.makedirs(common.clustering_base_path + 'unlimited_clusters/')

    # Placement Output Paths
    if not os.path.exists(common.placement_base_path):
        os.makedirs(common.placement_base_path)

    # Data Output Paths
    if not os.path.exists(common.data_base_path):
        os.makedirs(common.data_base_path)

    run()