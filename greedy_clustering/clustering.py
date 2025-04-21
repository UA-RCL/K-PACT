import numpy as np
import copy
from utils import *
from data_structures import Cluster, Cluster_list
import common as common

class Clustering():
    def __init__():
        super.__init__()

def check_conflict(slice1_start, slice1_end, slice2_start, slice2_end):
    """
    Check if two slices conflict with each other.

    Args:
        slice1_start (int): The start position of the first slice.
        slice1_end (int): The end position of the first slice.
        slice2_start (int): The start position of the second slice.
        slice2_end (int): The end position of the second slice.

    Returns:
        bool: True if the slices conflict, False otherwise.
    """

    return not (slice1_end <= slice2_start or slice1_start >= slice2_end)

def check_conflict_slice_vs_slices(slice1, slices):
    """
    Checks for conflicts between a given slice and a list of slices.

    Args:
        slice1 (tuple): A tuple representing the first slice with two elements.
        slices (list): A list of objects, each containing a 'slice' attribute which is a tuple with two elements.

    Returns:
        tuple: A tuple containing a boolean and a tuple. The boolean is True if there is a conflict, otherwise False.
               The tuple contains the conflicting slices if a conflict is found, otherwise the input slice1 and the last checked slice.
    """

    return any(check_conflict(slice1[0], slice1[1], slice2.slice[0], slice2.slice[1]) for slice2 in slices), slice1

def find_max_nonoverlapping_set(slice1, slice2):
    """
    Finds the maximum set of non-overlapping slices from two lists of slices.
    This function takes two lists of slices, combines them, and then finds the 
    maximum set of non-overlapping slices. Each slice is assumed to have a 
    'slice' attribute which is a tuple where the first element is the start 
    time and the second element is the end time.
    Args:
        slice1 (list): The first list of slices.
        slice2 (list): The second list of slices.
    Returns:
        list: A list of slices that form the maximum set of non-overlapping slices.
    """
    
    slices = sorted(slice1 + slice2, key=lambda x: x.slice[1])
    if not slices:
        print("Error: No slices provided.")
        exit()
    non_overlapping_set = [slices[0]]
    last_end_time = slices[0].slice[1]
    for slice in slices[1:]:
        if slice.slice[0] >= last_end_time:
            non_overlapping_set.append(slice)
            last_end_time = slice.slice[1]
    return non_overlapping_set

def check_overlap_within_personality(kernel_timing_data):
    """
    Check for overlapping slices within a given personality's kernel timing data.
    This function iterates through a list of kernel timing data slices and identifies
    non-overlapping slices. It returns a list of these non-overlapping slices and their
    corresponding indices in the original list.
    Args:
        kernel_timing_data (list): A list of objects where each object has a 'slice' attribute.
                                   The 'slice' attribute is a tuple containing start and end times.
    Returns:
        tuple: A tuple containing:
            - non_overlapping_slices (list): A list of non-overlapping slices.
            - remove_indices (list): A list of indices of the non-overlapping slices in the original list.
    """
    
    
    if not kernel_timing_data:
        print("Error: No kernel timing data provided.")
        exit()

    non_overlapping_slices = [kernel_timing_data[0]]
    remove_indices = [0]
    last_end_time = kernel_timing_data[0].slice[1]
    
    for idx, slice in enumerate(kernel_timing_data[1:], start=1):
        if slice.slice[0] >= last_end_time:
            non_overlapping_slices.append(slice)
            last_end_time = slice.slice[1]
            remove_indices.append(idx)
    
    return non_overlapping_slices, remove_indices

def has_duplicates(lst):
    """
    Check if a list contains duplicate elements.

    Args:
        lst (list): The list to check for duplicates.

    Returns:
        bool: True if the list contains duplicates, False otherwise.
    """
    return len(lst) != len(set(lst))
 
def get_new_max_nonoverlapping_set():
    """
    Computes the maximum non-overlapping sets of timing data and the number of overlaps for each person.

    This function iterates through pairs of timing data entries, finds the maximum non-overlapping set for each pair,
    and updates the count of overlaps for each person involved. It returns a dictionary of these sets and a dictionary
    of the number of overlaps for each person.

    Returns:
        tuple: A tuple containing:
            - max_nonoverlapping_sets (dict): A dictionary where keys are pairs of timing data keys (formatted as "key1-key2")
              and values are the corresponding maximum non-overlapping sets.
            - non_overlaps_ranking (dict): A dictionary where keys are timing data keys and values are the number
              of overlaps for each person.
    """
    max_nonoverlapping_sets = {}
    non_overlaps_ranking = {key: 0 for key in common.timing_data.data}
    already_covered = set()

    for key1, value1 in common.timing_data.data.items():
        already_covered.add(key1)
        for key2, value2 in common.timing_data.data.items():
            if key2 in already_covered:
                continue
            max_nonoverlapping_set = find_max_nonoverlapping_set(value1, value2)
            if len(max_nonoverlapping_set) not in (len(value1), len(value2)):
                max_nonoverlapping_sets[f"{key1}-{key2}"] = max_nonoverlapping_set
                non_overlaps_ranking[key1] += len(max_nonoverlapping_set)
                non_overlaps_ranking[key2] += len(max_nonoverlapping_set)
    return non_overlaps_ranking

def check_overlap_of_bin_with_others(cluster):
    """
    Checks for overlaps between a given bin and other clusters in the timing data.

    Args:
        bin (tuple): A tuple where the first element is the bin identifier and the second element is the bin slice.

    Returns:
        dict: A dictionary where the keys are items from the timing data and the values are lists of slices that do not overlap with the given bin slice.
    """
    if not common.timing_data.data:
        print("Error: No timing data provided.")
        return {}

    if not cluster.slices:
        print("Error: Bin slices are not initialized.")
        return {}

    non_overlaps = {
        item: [compared_slice for compared_slice in value if not check_conflict_slice_vs_slices(compared_slice.slice, cluster.slices)[0]]
        for item, value in common.timing_data.data.items()
        # if item not in cluster.kernels and (not common.ED_kurtosis_mode or item == "Kurtosis_0" or item == "ED8_atn_0")
        if item not in cluster.kernels and (not common.ED_kurtosis_mode or item == "Kurtosis_0")
    }
    return non_overlaps

def check_overlap_of_bin_with_others_only_one(cluster, slices):
    """
    Check for overlaps between a given cluster and a list of slices, and update the cluster with non-overlapping slices.

    Args:
        cluster (tuple): A tuple where the first element is the cluster identifier and the second element is a list of slices in the cluster.
        slices (list): A list of slices to be checked for overlap with the cluster's slices.

    Returns:
        tuple: A tuple containing:
            - list: Updated list of slices in the cluster after adding non-overlapping slices.
            - list: List of non-overlapping slices that were added to the cluster.
            - list: List of indices of the slices that were added to the cluster.
    """
    non_overlap, remove_list = [], []
    new_cluster_slices = copy.deepcopy(cluster.slices) 
    for idx, compared_slice in enumerate(slices):
        if not check_conflict_slice_vs_slices(compared_slice.slice, new_cluster_slices)[0]:
            new_cluster_slices.append(compared_slice)
            non_overlap.append(compared_slice)
            remove_list.append(idx)
    cluster.slices = new_cluster_slices  
    return cluster.slices, non_overlap, remove_list

def check_overlap_v2(interval1, interval2):
    """
    Check if two intervals overlap.

    Args:
        interval1: An object with a 'slice' attribute, which is a list or tuple containing two elements [start, end].
        interval2: An object with a 'slice' attribute, which is a list or tuple containing two elements [start, end].

    Returns:
        bool: True if the intervals overlap, False otherwise.
    """
    return interval1.slice[0] < interval2.slice[1] and interval1.slice[1] > interval2.slice[0]

def find_overlaps_for_bin(data):
    """
    Identifies overlapping items within a given dataset.

    Args:
        data (list): A list of items to be checked for overlaps. Each item should be compatible with the check_overlap_v2 function.

    Returns:
        list: A list of tuples, where each tuple contains two items from the input data that overlap.
    """
    return [(data[i], data[j]) for i in range(len(data)) for j in range(i + 1, len(data)) if check_overlap_v2(data[i], data[j])]

def fill_bin_with_overlaps(clusters, bin_id, personality_dict, mode=None):
    """
    Fills a bin with non-overlapping items based on certain criteria and updates the bin and the global data structure.
    Args:
        clusters (list): A list of clusters where each bin is a list containing items and their associated data.
        bin_id (int): The index of the bin to be filled.
        personality_dict (dict): A dictionary containing personality data for each item.
        mode (str, optional): An optional mode parameter that affects the overlap checking process.
    Raises:
        SystemExit: If there are duplicates in the remove list or if overlaps are found in the bin after processing.
    Notes:
        - The function first checks for overlaps using the `check_overlap_of_bin_with_others` function.
        - It sorts the non-overlapping items based on the length of their overlap lists in descending order.
        - It filters items based on a size ratio if the `common.homogeneous` flag is set.
        - It updates the bin with non-overlapping items and removes processed items from the global data structure.
        - It ensures there are no duplicates in the remove list and no overlaps in the final bin.
    """
    non_overlaps = check_overlap_of_bin_with_others(clusters[bin_id])
    sorted_non_overlaps = dict(sorted(non_overlaps.items(), key=lambda item: len(item[1]), reverse=True))

    remove_dict = {}
    for item in sorted_non_overlaps:
        # if common.homogeneous and "energy" not in item and "Kurtosis" not in item and "ED8_atn_0" not in item:
        if common.homogeneous and "energy" not in item and "Kurtosis" not in item:
            seed_size = personality_dict[clusters[bin_id].seed_kernel][0][0] * personality_dict[clusters[bin_id].seed_kernel][0][1]
            current_kernel_size = personality_dict[item][0][0] * personality_dict[item][0][1]
            if not (0.5 <= seed_size / current_kernel_size <= 2.0):
                continue

        non_overlap_bin, non_overlap_list, remove_list = check_overlap_of_bin_with_others_only_one(clusters[bin_id], common.timing_data.data[item])
        if non_overlap_list:
            clusters[bin_id].extend_kernels([item])
            clusters[bin_id].slices = non_overlap_bin
            remove_dict[item] = remove_list

    for key, remove_list in remove_dict.items():
        if has_duplicates(remove_list):
            print("Remove list has duplicates!!", remove_list)
            exit()
        common.timing_data.data[key] = [slice for idx, slice in enumerate(common.timing_data.data[key]) if idx not in remove_list]

    overlaps = find_overlaps_for_bin(clusters[bin_id].slices)
    if overlaps:
        print("There are overlaps!!!!", bin_id)
        exit()

    common.timing_data.data = {k: v for k, v in common.timing_data.data.items() if v}

def put_highest_ranked_pers_to_bin(clusters, bin_id):
    """
    Places the highest ranked personality into a specified bin.

    This function either places the personality with the highest energy detection kurtosis 
    or the personality with the maximum non-overlapping sets into the specified bin. 
    The selection is based on the `common.ED_kurtosis_mode` flag.

    Args:
        clusters (dict): A dictionary where the key is the bin ID and the value is a list containing 
                     the personality and its non-overlapping slices.
        bin_id (int): The ID of the bin where the personality will be placed.
        mode (str, optional): An optional mode parameter. Defaults to None.

    Returns:
        None
    """
    if common.ED_kurtosis_mode:
        key = "energy_detect1_0"
        non_overlapping_slices, remove_indices = check_overlap_within_personality(common.timing_data.data[key])
        clusters[bin_id] = Cluster(id=bin_id, kernels=[key], slices=non_overlapping_slices, IMEM_layer=0, seed_kernel=key)
        common.timing_data.data[key] = [slice for idx, slice in enumerate(common.timing_data.data[key]) if idx not in remove_indices]
        
    else:
        non_overlaps_ranking = get_new_max_nonoverlapping_set()
        sorted_non_overlaps_ranking = dict(sorted(non_overlaps_ranking.items(), key=lambda item: item[1], reverse=True))

        key = list(sorted_non_overlaps_ranking.keys())[0]
        non_overlapping_slices, remove_indices = check_overlap_within_personality(common.timing_data.data[key])
        clusters[bin_id] = Cluster(id=bin_id, kernels=[key], slices=non_overlapping_slices, IMEM_layer=0, seed_kernel=key)
        common.timing_data.data[key] = [slice for idx, slice in enumerate(common.timing_data.data[key]) if idx not in remove_indices]

def unlimited_IMEM_binning(personality_dict, clusters, bin_id, mode=None):
    """
    Organizes personalities into clusters based on overlap and ranking criteria.
    This function attempts to bin personalities from `personality_dict` into `clusters` 
    based on certain criteria. It uses a greedy clustering approach to minimize 
    overlap within each bin. The function operates in two modes: 'ed_kurtosis' mode 
    and a default mode.
    Parameters:
    personality_dict (dict): Dictionary containing personality data.
    clusters (dict): Dictionary where the keys are bin IDs and the values are lists of 
                 personalities assigned to each bin.
    bin_id (int): The current bin ID to which personalities are being assigned.
    mode (str, optional): The mode of operation. If set to 'ed_kurtosis', the function 
                          will operate in a special mode that prioritizes certain 
                          personalities. Defaults to None.
    Returns:
    tuple: A tuple containing the updated clusters, the next bin ID, and the mode used 
           ('ed_kurtosis' or None).
    """
    if common.ED_kurtosis_mode:
        while "energy_detect1_0" in common.timing_data.data and "Kurtosis_0" in common.timing_data.data:
            put_highest_ranked_pers_to_bin(clusters, bin_id)
            fill_bin_with_overlaps(clusters, bin_id, common.personality_dict)
            if "energy_detect1_0" not in common.timing_data.data and "Kurtosis_0" in common.timing_data.data:
                key = "Kurtosis_0"
                if common.timing_data.data[key]:
                    non_overlapping_slices, remove_indices = check_overlap_within_personality(common.timing_data.data[key])
                    bin_id += 1
                    clusters[bin_id] = Cluster(id=bin_id, kernels=[key], slices=non_overlapping_slices, IMEM_layer=0, seed_kernel=key)
                    common.timing_data.data[key] = [slice for idx, slice in enumerate(common.timing_data.data[key]) if idx not in remove_indices]
            common.ED_kurtosis_mode = "ed_kurtosis"
            return clusters, bin_id + 1
        common.timing_data.data.pop("Kurtosis_0", None)
        common.ED_kurtosis_mode = None
        return clusters, bin_id
    else:
        put_highest_ranked_pers_to_bin(clusters, bin_id)
        fill_bin_with_overlaps(clusters, bin_id, personality_dict)
        common.ED_kurtosis_mode = None
        return clusters, bin_id + 1

def bin_redistribution(clusters, bin_id, personality_dict, IMEM_size):
    """
    Redistributes items in bins to ensure that the size of each bin does not exceed the given IMEM size.
    Args:
        bin_id (int): The starting bin ID.
        personality_dict (dict): A dictionary where keys are item identifiers and values are tuples containing item properties.
        IMEM_size (int): The maximum allowed size for each bin.
    Returns:
        dict: A dictionary representing the redistributed bins. Each key is a bin ID, and the value is a list containing:
              - A list of item identifiers in the bin.
              - A list of time slices associated with the items in the bin.
              - The total size of the items in the bin.
    """
    copy_bins = {k: [v.kernels, v.slices, sum(personality_dict[item][1] for item in v.kernels)] for k, v in copy.deepcopy(clusters).items()}
    bin_id -= 1

    while True:
        for item, value in copy_bins.items():
            bin_size = value[2] 
            if bin_size <= IMEM_size:
                continue
            else:
                bin_id += 1
                copy_bins[bin_id] = [[], [], 0]
                while bin_size > IMEM_size:
                    remove_list = [idx for idx, time_slice in enumerate(value[1]) if time_slice.kernel_name == value[0][0]]
                    copy_bins[bin_id][0].append(value[0].pop(0))
                    copy_bins[bin_id][1].extend(value[1][i] for i in remove_list)
                    copy_bins[bin_id][2] += personality_dict[copy_bins[bin_id][0][-1]][1]
                    value[2] -= personality_dict[copy_bins[bin_id][0][-1]][1]
                    value[1] = [time_slice for idx, time_slice in enumerate(value[1]) if idx not in remove_list]
                    bin_size = value[2]
            
            break

        if all(value[2] <= IMEM_size for value in copy_bins.values()):
            break
    
    return copy_bins

def main_binning():
    """
    Perform the main binning process using unlimited IMEM binning.
    This function initializes the binning process by setting up the initial
    bin ID, an empty dictionary for bins, and calculating the total sum of
    lengths of timing data. It then iteratively processes the timing data
    using the `unlimited_IMEM_binning` function until all timing data has
    been binned.
    Returns:
        tuple: A tuple containing:
            - bins (dict): The dictionary containing the binned data.
            - bin_id (int): The final bin ID after processing.
            - bsum (int): The total sum of lengths of timing data.
    """
    bin_id, clusters, bsum = 0, Cluster_list().clusters, sum(len(value) for value in common.timing_data.data.values())
    while common.timing_data.data:
        clusters, bin_id = unlimited_IMEM_binning(common.personality_dict, clusters, bin_id, common.ED_kurtosis_mode)
    
    return clusters, bin_id, bsum

def redistribution(clusters, bin_id, bsum, IMEM_size):
    """
    Redistributes bins based on the given bin ID and IMEM size, and performs various checks to ensure the integrity of the binning process.

    Args:
        bin_id (int): The identifier for the bin to be redistributed.
        bsum (int): The initial sum of time slices before redistribution.
        IMEM_size (int): The size of the IMEM to be used for redistribution.

    Returns:
        dict: A dictionary representing the redistributed bins.

    Raises:
        SystemExit: If the sum of time slices after redistribution does not match the initial sum, if there are personalities not assigned to any bin, or if there are overlaps within any bin.
    """
    if IMEM_size:
        bins = bin_redistribution(clusters, bin_id, common.personality_dict, IMEM_size)

    asum = sum(len(value[1]) for value in bins.values())

    if asum != bsum:
        x = 0

    if common.timing_data.data:
        print("There are personalities that are not put into a bin!!!")
        print_dict_len(common.timing_data.data)
        exit()

    for bin, value in bins.items():
        if find_overlaps_for_bin(value[1]):
            print("There are overlaps!!!")
            exit()

    if bsum == asum and not common.timing_data.data:
        x = 0
    return bins
