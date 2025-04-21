# This sweep file includes experiments for tradeoff between IMEM size and PE array size
import os
import sys
import json
import copy
import common as common
import concurrent.futures
sys.path.append('.')

from greedy_clustering.clustering import main_binning, redistribution

def process_imem_size(clusters, IMEM_size, bin_id, bsum, array_id = None, array_count = None):
    common.current_IMEM_size = IMEM_size
    bins = redistribution(clusters, bin_id, bsum, IMEM_size)

    save_copy = copy.deepcopy(bins)

    # Remove the second item from each bin's value
    for key, value in save_copy.items():
        for idx, item in enumerate(value[1]):
            value[1][idx] = item.slice
        # value.pop(1)

    output_file_path = f"{common.redistributed_clusters_path}{int(IMEM_size / 8)}_lines_" + str(array_count) + "_arrays_id_" + str(array_id) + ".json"
    # Dump each clustering of IMEM size to a JSON file
    with open(output_file_path, 'w') as json_file:
        json.dump(save_copy, json_file, indent=2)

def IMEM_sweep(array_id=None, array_count=None):
    # Perform the clustering assuming IMEM size is unlimited
    clusters, bin_id, bsum = main_binning()

    save_copy = copy.deepcopy(clusters)            

    clusters_kernel_mapping = {}
    for id in clusters:
        clusters_kernel_mapping[id] = clusters[id].kernels

    # Save unlimited clustering to a json file
    with open(common.unlimited_clusters_path + 'unlimited_clusters_' + str(array_count) + "_arrays_id_" + str(array_id) + '.json', 'w') as json_file:
        json.dump(clusters_kernel_mapping, json_file, indent=2)

    # Start the clipping for each IMEM size
    with concurrent.futures.ProcessPoolExecutor(max_workers=common.number_of_workers) as executor:
        futures = {executor.submit(process_imem_size, clusters, IMEM_size, bin_id, bsum, array_id, array_count): IMEM_size for IMEM_size in common.IMEM_size_list}

        for future in concurrent.futures.as_completed(futures):
            future.result()
    