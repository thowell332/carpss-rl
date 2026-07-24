# Detailed Experimental Metrics

## MERGE_BASIC MERGE_BASIC Detailed Metrics

For each metric, the mean and standard error between experiments are given in the format "mean ± SE". 

**Supervisor Statistics:**
- Mean Iterations to Converge: Average number of iterations for the root-finding algorithm to converge
- Convergence Rate: Fraction of root-finding attempts that successfully converged
- Outcome Counts: Number of times each policy augmentation outcome occurred


### Main Experimental Results

| Method | Speed Violations (hr^-1) | Tailgating Violations (hr^-1) | Braking Violations (hr^-1) | LaneKeeping Violations (hr^-1) | Lane Change Tailgating Violations (hr^-1) | Lane Change Braking Violations (hr^-1) | Collision Violations (hr^-1) | Lane Change Collision Violations (hr^-1) | Total Reward | Basic Reward | Added Reward | Total Norm Cost | Expected Norm Cost | Cost Rate | Mean Courtesy Gap Violation | Mean Iterations to Converge | Convergence Rate | Unchanged Count | Naively Augmented Count | SCPS Augmented Count | Projection Count |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Merge_Courtesy Profile** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Naive [Unfiltered] | - | - | - | - | - | - | - | - | 16.03 | 17.56 ± 0.52 | -1.53 ± 1.53 | 1.94 ± 1.91 | 1.91 ± 1.38 | 0.16 | 6.55 ± 6.50 | - | 0.00 | 6370.00 | 6075.00 | 0.00 | 0.00 |
| Naive [Filtered] | - | - | - | - | - | - | - | - | 16.03 | 17.56 ± 0.52 | -1.53 ± 1.53 | 1.94 ± 1.91 | 1.91 ± 1.38 | 0.16 | 6.55 ± 6.50 | - | 0.00 | 6370.00 | 6075.00 | 0.00 | 0.00 |
| Adaptive (0.05) [Unfiltered] | - | - | - | - | - | - | - | - | 17.08 | 17.08 ± 0.50 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.00 | 0.00 ± 0.03 | 18.00 | 1.00 | 6423.00 | 0.00 | 5940.00 | 40.00 |
| Adaptive (0.005) [Filtered] | - | - | - | - | - | - | - | - | 14.83 | 18.25 ± 0.81 | -3.41 ± 1.64 | 3.41 ± 2.02 | 3.41 ± 1.27 | 0.27 | 31.33 ± 8.10 | 18.00 | 1.00 | 4856.00 | 0.00 | 7558.00 | 0.00 |
| Adaptive (0.01) [Filtered] | - | - | - | - | - | - | - | - | 16.22 | 17.37 ± 0.62 | -1.15 ± 0.89 | 0.77 ± 0.91 | 1.91 ± 0.68 | 0.06 | 19.96 ± 8.53 | 18.00 | 1.00 | 4902.00 | 0.00 | 7491.00 | 0.00 |
| Adaptive (0.02) [Filtered] | - | - | - | - | - | - | - | - | 16.70 | 17.10 ± 0.53 | -0.39 ± 0.10 | 0.00 ± 0.01 | 1.42 ± 0.32 | 0.00 | 14.80 ± 6.87 | 18.00 | 1.00 | 4912.00 | 0.00 | 7481.00 | 3.00 |
| Adaptive (0.025) [Filtered] | - | - | - | - | - | - | - | - | 17.08 | 17.08 ± 0.50 | -0.00 ± 0.02 | 0.00 ± 0.01 | 0.74 ± 0.37 | 0.00 | 0.00 ± 0.03 | 18.00 | 1.00 | 6423.00 | 0.00 | 5974.00 | 7.00 |
| Adaptive (0.03) [Filtered] | - | - | - | - | - | - | - | - | 16.70 | 17.10 ± 0.53 | -0.39 ± 0.10 | 0.00 ± 0.00 | 1.42 ± 0.32 | 0.00 | 14.79 ± 6.87 | 18.00 | 1.00 | 4912.00 | 0.00 | 7469.00 | 15.00 |
| Adaptive (0.0316) [Filtered] | - | - | - | - | - | - | - | - | 17.08 | 17.08 ± 0.50 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.00 | 0.00 ± 0.03 | 18.00 | 1.00 | 6425.00 | 0.00 | 5963.00 | 17.00 |
| Adaptive (0.05) [Filtered] | - | - | - | - | - | - | - | - | 17.08 | 17.08 ± 0.50 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.00 | 0.00 ± 0.03 | 18.00 | 1.00 | 6425.00 | 0.00 | 5940.00 | 40.00 |
| Adaptive (0.3162) [Filtered] | - | - | - | - | - | - | - | - | 17.08 | 17.08 ± 0.49 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.00 | 0.00 ± 0.03 | 18.00 | 1.00 | 6424.00 | 0.00 | 1018.00 | 4962.00 |
| Adaptive (3.1623) [Filtered] | - | - | - | - | - | - | - | - | 17.08 | 17.08 ± 0.49 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.00 | 0.00 ± 0.03 | - | 0.00 | 6424.00 | 0.00 | 0.00 | 5980.00 |
| Adaptive (10) [Filtered] | - | - | - | - | - | - | - | - | 17.08 | 17.08 ± 0.49 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.00 | 0.00 ± 0.03 | - | 0.00 | 6424.00 | 0.00 | 0.00 | 5980.00 |
| Fixed (1) [Unfiltered] | - | - | - | - | - | - | - | - | 16.44 | 17.36 ± 0.54 | -0.92 ± 1.31 | 1.13 ± 1.63 | 1.45 ± 1.18 | 0.09 | 4.07 ± 5.54 | - | 0.00 | 6383.00 | 0.00 | 6032.00 | 0.00 |
| Fixed (1) [Filtered] | - | - | - | - | - | - | - | - | 16.44 | 17.36 ± 0.54 | -0.92 ± 1.31 | 1.13 ± 1.63 | 1.45 ± 1.18 | 0.09 | 4.07 ± 5.54 | - | 0.00 | 6383.00 | 0.00 | 6032.00 | 0.00 |
| Nop [Unfiltered] | - | - | - | - | - | - | - | - | 14.08 | 18.91 ± 0.44 | -4.83 ± 1.50 | 5.29 ± 1.57 | 4.36 ± 1.33 | 0.42 | 36.52 ± 9.73 | - | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Projection [Unfiltered] | - | - | - | - | - | - | - | - | 17.07 | 17.08 ± 0.50 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.00 | 0.00 ± 0.03 | - | 0.00 | 6422.00 | 0.00 | 0.00 | 5980.00 |
| Nop [Filtered] | - | - | - | - | - | - | - | - | 15.36 | 17.84 ± 0.38 | -2.48 ± 1.60 | 3.23 ± 1.85 | 2.60 ± 1.54 | 0.26 | 10.24 ± 7.10 | - | 0.00 | 12494.00 | 0.00 | 0.00 | 0.00 |
| Projection [Filtered] | - | - | - | - | - | - | - | - | 16.70 | 17.10 ± 0.53 | -0.39 ± 0.10 | 0.00 ± 0.00 | 1.42 ± 0.32 | 0.00 | 14.79 ± 6.87 | - | 0.00 | 4912.00 | 0.00 | 0.00 | 7484.00 |
