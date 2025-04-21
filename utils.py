import pandas as pd
import ast
import json
import copy
import os

import common as common
from data_structures import *

kernel_key_list = {    "Kurtosis_0"        : ["Kurtosis1_b1", "Kurtosis2_b1"], 
                            "AEP_det_0"         : ["AEPDet_b1"], 
                            "AEP_bf_0"          : ["AEPbf_b1"], 
                            "CPDet_0"           : ["CPDet1_b1"], 
                            "CPDet_1"           : ["CPDet1_b1"], 
                            "ChirpDet_0"        : ["ChirpDet_b1", "ChirpDet2_b1"], 
                            "ChirpDet_1"        : ["ChirpDet_b1", "ChirpDet2_b1"], 
                            "OFDMEst_0"         : ["OFDMEst1"], 
                            "CREst_0"           : ["CREst1", "CREst2"], 
                            "energy_detect_0"   : ["ED1_b2", "ED2_b2", "ED3_b2", "ED4_b2", "ED5_b2", "ED6_b2", "ED7_b2", "ED8_b2"],
                            "energy_detect_1"   : ["ED1_b2", "ED2_b2", "ED3_b2", "ED4_b2", "ED5_b2", "ED6_b2", "ED7_b2", "ED8_b2"],
                            "energy_detect_2"   : ["ED1_b2", "ED2_b2", "ED3_b2", "ED4_b2", "ED5_b2", "ED6_b2", "ED7_b2", "ED8_b2"],
                            "energy_detect_3"   : ["ED1_b2", "ED2_b2", "ED3_b2", "ED4_b2", "ED5_b2", "ED6_b2", "ED7_b2", "ED8_b2"],
                            "energy_detect_4"   : ["ED1_b2", "ED2_b2", "ED3_b2", "ED4_b2", "ED5_b2", "ED6_b2", "ED7_b2", "ED8_b2"],
                            "energy_detect1_0"  : ["ED1_b1"],
                            "KTInstAmp_0"       : ["KTInstAmp_b1"], 
                            # "KTInstAmp_1"       : ["KTInstAmp_b1"],
                            "FSK_Est_0"         : ["FSK_Est_b1"], 
                            "FM_Est_0"          : ["FM_Est_b1"], 
                            "PSK_Est_0"         : ["PSK_Est_b1"],
                            "Cumulant42_0"      : ["Cumulant42_b1"], 
                            "Cumulant63_0"      : ["Cumulant63_b1"], 
                            "FSK_Det_0"         : ["FSK_Det_b1"], 
                            "BPSK_Det_0"        : ["BPSK_Det_b1"], 
                            "BPSK_Est_0"        : ["BPSK_Est_b1"], 
                            "MaxPSDDet_0"       : ["MaxPSDDet_b1"], 
                            # "MaxPSDDet_1"       : ["MaxPSDDet_b1"], 
                            "InstAmp_0"         : ["InstAmp_b1"], 
                            "QAM_Est_0"         : ["QAM_Est_b1"], 
                            "SpecCentroid_0"    : ["SpecCentroid_b1"], 
                            # "SpecCentroid_1"    : ["SpecCentroid_b1"], 
                            "PSK_Det_0"         : ["PSK_Det_b1"], 
                            "Cumulant40"      : ["Cumulant40_b1"], 
                            "DOA"             : ["DOA_b1"], 
                            "ED8_atn_0"             : ["ED8_atn"], 
                            "PSK_Est_cyclo_0"             : ["PSK_Est_cyclo"], 
                            "FSK_Est_cyclo_0"             : ["FSK_Est_cyclo"], 
                            "OFDM_Est_cyclo_0"             : ["OFDM_Est_cyclo"], 
                            }

def custom_key(item):
    if isinstance(item.slice[0], (int, float)):
        return int(item.slice[0])  
    elif isinstance(item[0], list):
        return int(item[0][0])

def process_timing_data(personality_dict, array_count=None):

    copy_timing_data = copy.deepcopy(common.timing_data.data)

    new_timing_data = {}

    for array_id in range(array_count):
        new_timing_data[array_id] = {}
        for key, value in kernel_key_list.items():
            new_timing_data[array_id][key] = []

    for new_timing_data_key, new_timing_data_value in kernel_key_list.items():
        for keys_to_search in new_timing_data_value:
            if keys_to_search in copy_timing_data.keys():
                for timing_item in common.timing_data.data[keys_to_search]:
                    slice_kernel_shape = (timing_item[3][0], int(timing_item[3][1]))
                    if personality_dict[new_timing_data_key][0] == slice_kernel_shape:
                        s = Slice(new_timing_data_key, timing_item[0], timing_item[1], int(timing_item[2]), slice_kernel_shape)
                        new_timing_data[timing_item[4]][new_timing_data_key].append(s)

    copy_new_timing_data = copy.deepcopy(new_timing_data)

    for array_id in range(array_count):
        for key, value in new_timing_data[array_id].items():
            if len(value) == 0:
                copy_new_timing_data[array_id].pop(key)
        
    new_timing_data = copy_new_timing_data

    common.timing_data.data = new_timing_data

    for array_id in range(array_count):
        for key, value in common.timing_data.data[array_id].items():
            common.timing_data.data[array_id][key] = sorted(value, key=custom_key)

def preprocess(timing_file_path=None, array_count=None): 
    csv_file = pd.read_csv('ACC_model.csv')

    pers_list = []
    for index, entry in csv_file.iterrows():
        # print(entry)
        # print(entry['PE shape'])
        if entry['PE shape'].split(';')[0] == "0,0":
            continue
        pers_list.append(str(entry['Config']))

    personality_dict = {}
    for key in pers_list:
        key_id = 0
        for index, entry in csv_file.iterrows():
            kernel_name = entry['Config']

            if key == kernel_name:
                for partitioned_shape in entry['PE shape'].split(';'):
                    personality_dict[key + "_" + str(key_id)] = [ast.literal_eval(partitioned_shape), entry['Instructions'] * 8]
                    key_id += 1
    
    if timing_file_path != None:
        with open(timing_file_path, 'r') as file:
            common.timing_data.data = json.load(file)

        process_timing_data(personality_dict, array_count)

    if timing_file_path != None:
        return personality_dict
    else:
        return personality_dict

def IMEM_area_calculation(IMEM_size, number_of_PEs):
    # Initial PE area for 64 lines of IMEM for only one PE
    baseline_IMEM_size = 64
    initial_IMEM_area = 1362.72
    increment_for_1line_IMEM = 6.90
    return (initial_IMEM_area * ((IMEM_size - baseline_IMEM_size) * increment_for_1line_IMEM)) * number_of_PEs

def PE_array_area_calculation(IMEM_size, number_of_PEs):
    # Initial PE area for 64 lines of IMEM for only one PE
    baseline_IMEM_size = 64
    initial_PE_area = 56800
    increment_for_1line_IMEM = 21.875

    # Find the increase in IMEM size compared to baseline
    IMEM_diff = IMEM_size - baseline_IMEM_size
    # Calculate the area increase for 1 PE
    increment = IMEM_diff * increment_for_1line_IMEM
    # Add it to area for 1 PE
    area_for_1PE = initial_PE_area + increment
    # Multiply number of PEs with area for 1 PE
    total_area = area_for_1PE * number_of_PEs
    return total_area

def row_buffer_area_calculation(number_of_rows):
    # Estimation for the area increase when we add 1 more input-output pair (in terms of um2)
    scale = 8.627
    return float(number_of_rows * number_of_rows * scale)

def calculate_IMEM_sizes():
    for i in range(common.number_of_IMEM_sizes):
        common.IMEM_size_list.append((320 + i * 64) * 8)
        common.IMEM_size_list_lines.append((320 + i * 64))
        common.IMEM_size_list_KB.append(((320 + i * 64) * 8) / 1024)
    return common.IMEM_size_list, common.IMEM_size_list_lines, common.IMEM_size_list_KB

def print_dict(dict):
    for key, value in dict.items():
        print(key, ":", value)

def print_dict_len(dict):
    for key, value in dict.items():
        print(key, ":", len(value))

def print_dict_size(dict):
    total_number = 0
    for key, value in dict.items():
        total_number += len(value)
    print("There are", total_number, "timing slices")

def print_bins(dict):
    for key, value in dict.items():
        print(key, ":", value[0], ", ", len(value[1]), ", ", value[2], ", ", value[3].shape)

def print_bin(id, bin):
    print(id, ":", bin[0], ", ", len(bin[1]), ", ", bin[2], ", ", bin[3].shape)
