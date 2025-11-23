# K-PACT: Kernel Planning for Adaptive Context Switching — A Framework for Clustering, Placement, and Prefetching in Spectrum Sensing

- This repository contains the official implementation of ***K-PACT: Kernel Planning for Adaptive Context Switching — A Framework for Clustering, Placement, and Prefetching in Spectrum Sensing*** , which is published in ICCAD25. The paper is available in [IEEExplore](https://ieeexplore.ieee.org/document/11240855).

## Code Structure

<pre>
- greedy_clustering/ : Contains the clustering/placement algorithm 
- output/            : Contains sample output data
- scripts/           : Contains scripts driving the clustering/placement sweep
- ACC_model.csv      : Contains kernel information
- common.py          : Contains common variables for the environment
- data_structures.py : Contains simple data structures
- input_data.json    : Contains sample input data
- main.py            : Contains source code driving the whole flow and for input arguments 
- requirements.txt   : Contains python/conda environment requirements 
- utils.py           : Contains necessary utility functions
</pre>

## Installation Instructions

- Create a python environment install the required libraries:
```bash
python3 -m venv <env_path>
source <env_path>/bin/activate
pip3 install -r requirements.txt
```

## Standalone Experiment

- Run following commands for standalone experiment that uses a sample input data
```bash
python3 main.py
```

- See the possible options
```bash
python3 main.py -h
```

- Possible options are:
<pre>
--array_count           : number of arrays to place clusters
--initial_array_size    : array size that data is collected with 
--number_of_IMEM_sizes  : number of IMEM size to sweep 
--number_of_trees       : number of trees in the workload 
--number_of_subbands    : number of subbands in the workload
--heterogeneity_type    : setting 1 takes kernel shapes into account to reduce resource underutilization
--ED_kurtosis_mode      : setting 1 clusters ED and Kurtosis together exclusively, and places close to SRAM
--parallelization       : setting 1 enables parallelization with multiple processes
--number_of_workers     : number of threads if parallelization is enabled
--output_dir            : directory to store output files
</pre>

## Citation

If used for research, please cite K-PACT by the following publication:

```
@INPROCEEDINGS{11240855,
  author={Suluhan, H. Umut and Lin, Jiahao and Gener, Serhan and Chakrabarti, Chaitali and Ogras, Umit and Akoglu, Ali},
  booktitle={2025 IEEE/ACM International Conference On Computer Aided Design (ICCAD)}, 
  title={K-PACT: Kernel Planning for Adaptive Context Switching — A Framework for Clustering, Placement, and Prefetching in Spectrum Sensing}, 
  year={2025},
  volume={},
  number={},
  pages={1-9},
  keywords={Context;Runtime;Heuristic algorithms;Switches;Software;Hardware;Sensors;Planning;Kernel;Low latency communication;systolic array;clustering;placement;dynamic switching},
  doi={10.1109/ICCAD66269.2025.11240855}}

```