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
| Naive [Unfiltered] | - | - | - | - | - | - | - | - | 55.03 | 38.60 ± 5.45 | 16.43 ± 5.14 | 5.75 ± 9.36 | 8.75 ± 8.12 | 0.15 | - | 0.00 | 0.00 | 38604.00 | - | 0.00 |
| Naive [Filtered] | - | - | - | - | - | - | - | - | 55.73 | 39.14 ± 4.52 | 16.59 ± 5.01 | 5.95 ± 9.38 | 8.97 ± 8.10 | 0.15 | - | 0.00 | 0.00 | 39139.00 | - | 0.00 |
| Adaptive (0.05) [Unfiltered] | - | - | - | - | - | - | - | - | 56.51 | 38.10 ± 6.41 | 18.40 ± 3.36 | 1.30 ± 2.60 | 5.23 ± 2.93 | 0.03 | 18.00 | 1.00 | 0.00 | 0.00 | - | 3310.00 |
| Adaptive (0.0316) [Filtered] | - | - | - | - | - | - | - | - | 57.95 | 39.33 ± 3.95 | 18.62 ± 2.60 | 2.10 ± 3.63 | 6.00 ± 3.73 | 0.05 | 18.00 | 1.00 | 0.00 | 0.00 | - | 2837.00 |
| Adaptive (0.05) [Filtered] | - | - | - | - | - | - | - | - | 57.72 | 38.96 ± 4.96 | 18.75 ± 2.74 | 1.46 ± 2.67 | 5.45 ± 2.98 | 0.04 | 18.00 | 1.00 | 0.00 | 0.00 | - | 3319.00 |
| Adaptive (0.3162) [Filtered] | - | - | - | - | - | - | - | - | 55.72 | 37.39 ± 7.90 | 18.33 ± 3.97 | 0.72 ± 1.50 | 4.69 ± 2.13 | 0.02 | 18.00 | 0.91 | 0.00 | 0.00 | - | 30670.00 |
| Adaptive (3.1623) [Filtered] | - | - | - | - | - | - | - | - | 55.28 | 37.08 ± 8.42 | 18.21 ± 4.22 | 0.66 ± 1.25 | 4.59 ± 1.95 | 0.02 | 18.00 | 0.17 | 0.00 | 0.00 | - | 36482.00 |
| Adaptive (10) [Filtered] | - | - | - | - | - | - | - | - | 54.75 | 36.84 ± 8.59 | 17.90 ± 4.38 | 1.03 ± 2.24 | 4.87 ± 2.62 | 0.03 | 18.00 | 0.11 | 0.00 | 0.00 | - | 36677.00 |
| Fixed (1) [Unfiltered] | - | - | - | - | - | - | - | - | 54.14 | 37.63 ± 6.81 | 16.51 ± 4.96 | 4.62 ± 8.22 | 7.77 ± 7.24 | 0.12 | - | 0.00 | 0.00 | 0.00 | - | 0.00 |
| Fixed (1) [Filtered] | - | - | - | - | - | - | - | - | 55.61 | 38.76 ± 5.22 | 16.85 ± 4.67 | 5.05 ± 8.34 | 8.23 ± 7.30 | 0.13 | - | 0.00 | 0.00 | 0.00 | - | 0.00 |
| Nop [Unfiltered] | - | - | - | - | - | - | - | - | 48.78 | 39.20 ± 4.44 | 9.57 ± 5.91 | 20.06 ± 12.08 | 19.91 ± 10.29 | 0.51 | - | 0.00 | 0.00 | 0.00 | - | 0.00 |
| Projection [Unfiltered] | - | - | - | - | - | - | - | - | 51.21 | 34.20 ± 10.92 | 17.02 ± 5.47 | 0.17 ± 0.24 | 3.88 ± 1.30 | 0.00 | - | 0.00 | 0.00 | 0.00 | - | 34196.00 |
| Nop [Filtered] | - | - | - | - | - | - | - | - | 48.78 | 39.20 ± 4.44 | 9.57 ± 5.91 | 20.06 ± 12.08 | 19.91 ± 10.29 | 0.51 | - | 0.00 | 0.00 | 0.00 | - | 0.00 |
| Projection [Filtered] | - | - | - | - | - | - | - | - | 54.46 | 36.75 ± 8.69 | 17.71 ± 4.53 | 1.33 ± 3.22 | 5.11 ± 3.39 | 0.04 | - | 0.00 | 0.00 | 0.00 | - | 36751.00 |
