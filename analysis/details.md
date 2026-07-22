# Detailed Experimental Metrics

## 3L30V 3L30V Detailed Metrics

For each metric, the mean and standard error between experiments are given in the format "mean ± SE". 

**Supervisor Statistics:**
- Mean Iterations to Converge: Average number of iterations for the root-finding algorithm to converge
- Convergence Rate: Fraction of root-finding attempts that successfully converged
- Outcome Counts: Number of times each policy augmentation outcome occurred


### Main Experimental Results

| Method | Speed Violations (hr^-1) | Tailgating Violations (hr^-1) | Braking Violations (hr^-1) | LaneKeeping Violations (hr^-1) | Lane Change Tailgating Violations (hr^-1) | Lane Change Braking Violations (hr^-1) | Collision Violations (hr^-1) | Lane Change Collision Violations (hr^-1) | Total Reward | Basic Reward | Added Reward | Total Norm Cost | Expected Norm Cost | Cost Rate | Mean Iterations to Converge | Convergence Rate | Unchanged Count | Naively Augmented Count | SCPS Augmented Count | Projection Count |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Right_Lane Profile** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Naive [Unfiltered] | - | - | - | - | - | - | - | - | 58.14 | 41.87 ± 6.24 | 16.27 ± 5.16 | 5.57 ± 9.19 | 8.62 ± 7.96 | 0.14 | - | 0.00 | 0.00 | 38523.00 | - | 0.00 |
| Naive [Filtered] | - | - | - | - | - | - | - | - | 59.00 | 42.53 ± 5.19 | 16.47 ± 5.02 | 5.81 ± 9.20 | 8.87 ± 7.94 | 0.15 | - | 0.00 | 0.00 | 39140.00 | - | 0.00 |
| Adaptive (0.05) [Unfiltered] | - | - | - | - | - | - | - | - | 59.08 | 40.85 ± 6.73 | 18.23 ± 3.27 | 1.27 ± 2.49 | 5.23 ± 2.81 | 0.03 | 18.00 | 1.00 | 0.00 | 0.00 | - | 3082.00 |
| Adaptive (0.0316) [Filtered] | - | - | - | - | - | - | - | - | 60.79 | 42.32 ± 4.25 | 18.47 ± 2.51 | 2.02 ± 3.42 | 5.96 ± 3.52 | 0.05 | 18.00 | 1.00 | 0.00 | 0.00 | - | 2601.00 |
| Adaptive (0.05) [Filtered] | - | - | - | - | - | - | - | - | 60.41 | 41.81 ± 5.11 | 18.60 ± 2.59 | 1.44 ± 2.57 | 5.47 ± 2.85 | 0.04 | 18.00 | 1.00 | 0.00 | 0.00 | - | 3094.00 |
| Adaptive (0.3162) [Filtered] | - | - | - | - | - | - | - | - | 58.29 | 40.05 ± 8.11 | 18.24 ± 3.84 | 0.72 ± 1.37 | 4.75 ± 2.03 | 0.02 | 18.00 | 0.91 | 0.00 | 0.00 | - | 30890.00 |
| Adaptive (3.1623) [Filtered] | - | - | - | - | - | - | - | - | 57.66 | 39.60 ± 8.84 | 18.06 ± 4.21 | 0.67 ± 1.28 | 4.65 ± 1.92 | 0.02 | 18.00 | 0.17 | 0.00 | 0.00 | - | 36588.00 |
| Adaptive (10) [Filtered] | - | - | - | - | - | - | - | - | 57.06 | 39.30 ± 9.01 | 17.76 ± 4.38 | 1.06 ± 2.33 | 4.94 ± 2.66 | 0.03 | 18.00 | 0.11 | 0.00 | 0.00 | - | 36805.00 |
| Fixed (1) [Unfiltered] | - | - | - | - | - | - | - | - | 57.49 | 41.04 ± 7.08 | 16.45 ± 4.88 | 4.50 ± 8.06 | 7.72 ± 7.08 | 0.12 | - | 0.00 | 0.00 | 0.00 | - | 0.00 |
| Fixed (1) [Filtered] | - | - | - | - | - | - | - | - | 59.02 | 42.22 ± 5.49 | 16.79 ± 4.61 | 4.95 ± 8.15 | 8.19 ± 7.12 | 0.13 | - | 0.00 | 0.00 | 0.00 | - | 0.00 |
| Nop [Unfiltered] | - | - | - | - | - | - | - | - | 53.22 | 43.59 ± 5.80 | 9.63 ± 5.93 | 19.82 ± 12.14 | 19.70 ± 10.34 | 0.51 | - | 0.00 | 0.00 | 0.00 | - | 0.00 |
| Projection [Unfiltered] | - | - | - | - | - | - | - | - | 53.50 | 36.63 ± 11.31 | 16.87 ± 5.41 | 0.16 ± 0.23 | 3.93 ± 1.29 | 0.00 | - | 0.00 | 0.00 | 0.00 | - | 34400.00 |
| Nop [Filtered] | - | - | - | - | - | - | - | - | 53.22 | 43.59 ± 5.80 | 9.63 ± 5.93 | 19.82 ± 12.14 | 19.70 ± 10.34 | 0.51 | - | 0.00 | 0.00 | 0.00 | - | 0.00 |
| Projection [Filtered] | - | - | - | - | - | - | - | - | 56.87 | 39.27 ± 8.98 | 17.60 ± 4.50 | 1.40 ± 3.50 | 5.23 ± 3.60 | 0.04 | - | 0.00 | 0.00 | 0.00 | - | 36992.00 |
