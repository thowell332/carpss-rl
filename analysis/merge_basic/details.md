# Detailed Experimental Metrics

## MERGE_BASIC MERGE_BASIC Detailed Metrics

For each metric, the mean and standard error between experiments are given in the format "mean ± SE". 

**Supervisor Statistics:**
- Mean Iterations to Converge: Average number of iterations for the root-finding algorithm to converge
- Convergence Rate: Fraction of root-finding attempts that successfully converged
- Outcome Counts: Number of times each policy augmentation outcome occurred


### Main Experimental Results

| Method | Speed Violations (hr^-1) | Tailgating Violations (hr^-1) | Braking Violations (hr^-1) | LaneKeeping Violations (hr^-1) | Lane Change Tailgating Violations (hr^-1) | Lane Change Braking Violations (hr^-1) | Collision Violations (hr^-1) | Lane Change Collision Violations (hr^-1) | Total Reward | Basic Reward | Added Reward | Total Norm Cost | Expected Norm Cost | Cost Rate | Mean Iterations to Converge | Convergence Rate | Unchanged Count | Naively Augmented Count | SCPS Augmented Count | Projection Count |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Merge_Courtesy Profile** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Adaptive (0.05) [Filtered] | - | - | - | - | - | - | - | - | 17.42 | 17.42 ± 0.76 | 0.00 ± 0.00 | 0.03 ± 0.20 | 0.44 ± 0.48 | 0.00 | 18.00 | 0.71 | 946.00 | 0.00 | 300.00 | 7.00 |
| Nop [Unfiltered] | - | - | - | - | - | - | - | - | 17.78 | 17.78 ± 0.65 | 0.00 ± 0.00 | 1.48 ± 1.42 | 1.01 ± 0.97 | 0.12 | - | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
