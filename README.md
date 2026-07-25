# State-Wise Constrained Policy Shaping: Runtime Behavior Steering for Safe Reinforcement Learning

This project contains all of the source code, raw results, and plots for the self-titled submission to AAAI-AIA-26.

## Table of Contents
- [1. Project Structure](#1-project-structure)
- [2. Getting Started](#2-getting-started)
- [3. Replication Instructions](#3-usage)
    - [3.1. Training Models](#31-training-models)
    - [3.2. Running Experiments](#32-running-experiments)
    - [3.3. Analyzing Results](#33-analyzing-results)

## 1. Project Structure

For convienence, the in-distribution environment with four lanes and 20 vehicles is referred to as `4L20V`; similarly, the complex zero-shot environment with six lanes and 50 vehicles is referred to as `6L50V` and the simple zero-shot environment with two lanes and ten vehicles is referred to as `2L10V`.

- [configs/](configs/) - Training and environment configuration files.
    - [environment/](configs/environment/) - Environment configurations for `4L20V`, `6L50V`, and `2L10V`. Note that all environment configurations are identical except for the number of lanes and the number of vehicles.
    - [training/](configs/training/) - Configuration for training the DQN model. All hyperparameter values are the defaults from Stable-Baselines3.
- [models/](models/) - The pre-trained DQN model used in all of our experiments. This model was trained in the `4L20V` environment with the default training configuration.
- [scps_supervisor/](scps_supervisor/) - Core package containing our implementation of the SCPS supervisor.
    - [supervisor.py](scps_supervisor/supervisor.py) - Main module for the SCPS supervisor implementation.
    - [norms/](scps_supervisor/norms/) - Norms package containing our implementation of norms and constraints.
    - [profiles/](scps_supervisor/norms/profiles/) - Profiles package containing our implementation of the behavior profiles.
- [scripts/](scripts/) - Useful scripts for training models, testing various methods, and debugging.
    - [train.py](scripts/train.py) - Train a new model using selected configuration files.
    - [test.py](scripts/test.py) - Test a pre-trained model with one of the available methods (unsupervised, filter-only, naive augment, fixed SCPS, adaptive SCPS, or cost-optimal projection).
    - [run_experiments.sh](scripts/run_experiments.sh) - Useful script for running multiple experiments and recording the results.
    - [analyze_results.py](scripts/analyze_results.py) - Analysis script for generating tables and plots from recorded results.
    - [debug_collision.py](scripts/debug_collision.py) - Debugging script for replaying a specific episode under the selected configuration with the GUI enabled.
- [results/](results/) - Raw CSV results, organized by domain:
    - [results/highway/](results/highway/) - Highway / complex zero-shot environment runs.
    - [results/merge/](results/merge/) - Merge-environment courtesy runs.
- [analysis/](analysis/) - Analysis generated from the raw results, organized the same way:
    - [analysis/highway/](analysis/highway/) - Tables and plots for highway.
    - [analysis/merge/](analysis/merge/) - Tables and plots for merge.

## 2. Getting Started

### 2.1. Prerequisites

- `python >= 3.9`
- `virtualenv` (recommended)

### 2.2. Installation

```bash
python -m venv venv
source venv/bin/activate
pip install .
```

## 3. Replication Instructions

This section describes the full set of instructions required to replicate all of the results presented in our paper.

### 3.1. Training Models

To train the base DQN model, run the `train.py` script. When prompted, choose the `default.json` training configuration and the `4_lanes_20_vehicles.json` environment configuration.

```bash
python scripts/train.py
```

### 3.2. Running Experiments

Using the model trained in the previous step, or the pre-trained model included in `models/4_lanes_20_vehicles.zip`, run the full suite of experiments specified in `run_experiments.sh`. Note that if the `results/` directory is already populated, you either need to clear the directory or set `FORCE_WRITE=true` in the shell script to overwrite existing results.

```bash
./run_experiments.sh <env>
```

If no environment is provided, this script will default to running the entire suite of experiments for all three environment configurations. Note that this may take awhile, especially as the complexity of the environment increases. The results will be written as CSV files to the `results/` directory, with sub-directories for each environment.

### 3.3. Analyzing Results

To analyze the collected data, you can either inspect the CSV files, or use the analysis script which is provided for convenience.

```bash
python scripts/analyze_results.py --results-dir results/highway --output-dir analysis/highway
python scripts/analyze_results.py --results-dir results/merge --output-dir analysis/merge
```

Summary statistics will be written to the specified directory. Most of the relevant information from the experimental data will be written to a `summary.md` file in the specified output directory. This file contains information about the collision rate, norm violation cost rate, and vehicle speed for all experimental configurations. Use `--help` to read all of the command-line options.
