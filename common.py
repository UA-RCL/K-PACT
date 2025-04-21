from data_structures import *
from datetime import datetime
import os

# Configurations
array_count = None
parallelization = None
number_of_workers = None

# Sweep Configurations
homogeneous = None
number_of_IMEM_sizes = None
IMEM_size_list = []
IMEM_size_list_lines = []
IMEM_size_list_KB = []

# Preprocess
subband_count = None
number_of_trees = None
initial_array_size = None
timing_data = Timing_Data()
personality_dict = []
IMEM_PE_area_mapping = []
interval_merging = None

# Clustering
ED_kurtosis_mode = None

# Output
base_path = 'output/'
# Clustering Output Paths
clustering_base_path = None #  base_path + '/clustering/'
redistributed_clusters_path = None #   clustering_base_path + '/redistributed_clusters/'
unlimited_clusters_path = None #   clustering_base_path + '/unlimited_clusters/'
# Placement Output Paths
placement_base_path = None #  base_path + '/placement/'
# Routing Output Paths
routing_base_path = None #  base_path + '/routing/'
# Data Output Paths
data_base_path = None #  base_path + '/data/'
# Plots Output Paths
plots_base_path = None #  base_path + '/plots/'

