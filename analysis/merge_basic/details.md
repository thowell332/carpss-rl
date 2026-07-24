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
| Naive [Unfiltered] | - | - | - | - | - | - | - | - | 13.72 | 17.62 ± 0.49 | -3.90 ± 1.72 | 4.07 ± 2.07 | 3.74 ± 1.37 | 0.33 | 33.19 ± 8.87 | - | 0.00 | 4855.00 | 7594.00 | 0.00 | 0.00 |
| Naive [Filtered] | - | - | - | - | - | - | - | - | 13.72 | 17.62 ± 0.49 | -3.90 ± 1.72 | 4.07 ± 2.07 | 3.74 ± 1.37 | 0.33 | 33.19 ± 8.87 | - | 0.00 | 4855.00 | 7594.00 | 0.00 | 0.00 |
| Adaptive (0.05) [Unfiltered] | - | - | - | - | - | - | - | - | 16.51 | 16.90 ± 0.43 | -0.39 ± 0.10 | 0.00 ± 0.00 | 1.42 ± 0.32 | 0.00 | 14.79 ± 6.87 | 18.00 | 1.00 | 4910.00 | 0.00 | 7445.00 | 39.00 |
| Adaptive (0.005) [Filtered] | - | - | - | - | - | - | - | - | 14.83 | 18.25 ± 0.81 | -3.41 ± 1.64 | 3.41 ± 2.02 | 3.41 ± 1.27 | 0.27 | 31.33 ± 8.10 | 18.00 | 1.00 | 4856.00 | 0.00 | 7558.00 | 0.00 |
| Adaptive (0.01) [Filtered] | - | - | - | - | - | - | - | - | 15.90 | 17.04 ± 0.45 | -1.15 ± 0.89 | 0.77 ± 0.91 | 1.91 ± 0.68 | 0.06 | 19.96 ± 8.53 | 18.00 | 1.00 | 4902.00 | 0.00 | 7491.00 | 0.00 |
| Adaptive (0.02) [Filtered] | - | - | - | - | - | - | - | - | 16.51 | 16.91 ± 0.43 | -0.39 ± 0.10 | 0.00 ± 0.01 | 1.42 ± 0.32 | 0.00 | 14.80 ± 6.87 | 18.00 | 1.00 | 4912.00 | 0.00 | 7481.00 | 3.00 |
| Adaptive (0.025) [Filtered] | - | - | - | - | - | - | - | - | 17.08 | 17.08 ± 0.50 | -0.00 ± 0.02 | 0.00 ± 0.01 | 0.74 ± 0.37 | 0.00 | 0.00 ± 0.03 | 18.00 | 1.00 | 6423.00 | 0.00 | 5974.00 | 7.00 |
| Adaptive (0.03) [Filtered] | - | - | - | - | - | - | - | - | 16.51 | 16.91 ± 0.43 | -0.39 ± 0.10 | 0.00 ± 0.00 | 1.42 ± 0.32 | 0.00 | 14.79 ± 6.87 | 18.00 | 1.00 | 4912.00 | 0.00 | 7469.00 | 15.00 |
| Adaptive (0.0316) [Filtered] | - | - | - | - | - | - | - | - | 17.08 | 17.08 ± 0.50 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.00 | 0.00 ± 0.03 | 18.00 | 1.00 | 6425.00 | 0.00 | 5963.00 | 17.00 |
| Adaptive (0.05) [Filtered] | - | - | - | - | - | - | - | - | 16.51 | 16.91 ± 0.43 | -0.39 ± 0.10 | 0.00 ± 0.00 | 1.42 ± 0.32 | 0.00 | 14.79 ± 6.87 | 18.00 | 1.00 | 4912.00 | 0.00 | 7445.00 | 39.00 |
| Adaptive (0.3162) [Filtered] | - | - | - | - | - | - | - | - | 17.08 | 17.08 ± 0.49 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.00 | 0.00 ± 0.03 | 18.00 | 1.00 | 6424.00 | 0.00 | 1018.00 | 4962.00 |
| Adaptive (3.1623) [Filtered] | - | - | - | - | - | - | - | - | 17.08 | 17.08 ± 0.49 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.00 | 0.00 ± 0.03 | - | 0.00 | 6424.00 | 0.00 | 0.00 | 5980.00 |
| Adaptive (10) [Filtered] | - | - | - | - | - | - | - | - | 17.08 | 17.08 ± 0.49 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.00 | 0.00 ± 0.03 | - | 0.00 | 6424.00 | 0.00 | 0.00 | 5980.00 |
| Fixed (1) [Unfiltered] | - | - | - | - | - | - | - | - | 14.14 | 17.48 ± 0.52 | -3.34 ± 1.65 | 3.31 ± 2.03 | 3.36 ± 1.26 | 0.27 | 30.94 ± 8.01 | - | 0.00 | 4874.00 | 0.00 | 7551.00 | 0.00 |
| Fixed (1) [Filtered] | - | - | - | - | - | - | - | - | 14.14 | 17.48 ± 0.52 | -3.34 ± 1.65 | 3.31 ± 2.03 | 3.36 ± 1.26 | 0.27 | 30.94 ± 8.01 | - | 0.00 | 4874.00 | 0.00 | 7551.00 | 0.00 |
| Nop [Unfiltered] | - | - | - | - | - | - | - | - | 13.01 | 17.84 ± 0.39 | -4.83 ± 1.50 | 5.29 ± 1.57 | 4.36 ± 1.33 | 0.42 | 36.52 ± 9.73 | - | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Projection [Unfiltered] | - | - | - | - | - | - | - | - | 16.51 | 16.90 ± 0.43 | -0.39 ± 0.10 | 0.00 ± 0.00 | 1.42 ± 0.32 | 0.00 | 14.79 ± 6.87 | - | 0.00 | 4910.00 | 0.00 | 0.00 | 7484.00 |
| Nop [Filtered] | - | - | - | - | - | - | - | - | 14.35 | 18.91 ± 0.55 | -4.56 ± 1.52 | 5.01 ± 1.58 | 4.12 ± 1.34 | 0.40 | 35.01 ± 10.05 | - | 0.00 | 2525.00 | 0.00 | 0.00 | 0.00 |
| Projection [Filtered] | - | - | - | - | - | - | - | - | 16.51 | 16.91 ± 0.43 | -0.39 ± 0.10 | 0.00 ± 0.00 | 1.42 ± 0.32 | 0.00 | 14.79 ± 6.87 | - | 0.00 | 4912.00 | 0.00 | 0.00 | 7484.00 |
