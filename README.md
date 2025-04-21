# Greedy Kernel Clustering/Placement on Systolic Array

- This folder contains the source code and input files for clustering and placement. 

## Installation

- Create a python environment install the required libraries:
```bash
python3 -m venv <env_path>
source <env_path>/bin/activate
pip3 install -r requirements.txt
```

## Code Structure

- ```greedy_clustering/``` : Contains the algorithm 
- ```scripts/```           : Contains scripts driving the clustering/placement sweep
- ```timing_files/```      : Contains input files
- ```utils/```             : Contains necessary utility functions
- ```common.py```          : Contains common variables for the environment
- ```data_structures.py``` : Contains simple data structures
- ```main.py```            : Contains source code driving the whole flow and for input arguments 

## Standalone Experiment

- Run following commands for standalone experiment 
```bash
python3 main.py
```

- See the possible options
```bash
python3 main.py -h
```

- Important options are
    - --homogeneous:      setting 1 takes kernel shapes into account
    - --ED_kurtosis_mode: setting 1 clusters ED and Kurtosis together exclusively