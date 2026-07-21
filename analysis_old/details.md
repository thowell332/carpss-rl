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
| Naive [Unfiltered] | - | - | - | - | - | - | - | - | 58.47 | 41.75 ± 5.98 | 16.72 ± 4.65 | 5.21 ± 8.18 | - | 0.13 | - | 0.00 | 0.00 | 38645.00 | - | 0.00 |
| Naive [Filtered] | - | - | - | - | - | - | - | - | 59.35 | 42.44 ± 4.67 | 16.90 ± 4.51 | 5.45 ± 8.26 | - | 0.14 | - | 0.00 | 0.00 | 39260.00 | - | 0.00 |
| Adaptive (0.05) [Unfiltered] | - | - | - | - | - | - | - | - | 59.60 | 40.96 ± 6.11 | 18.64 ± 3.00 | 1.21 ± 2.43 | - | 0.03 | 18.00 | 0.91 | 0.00 | 0.00 | - | 3459.00 |
| Adaptive (0.05) [Filtered] | - | - | - | - | - | - | - | - | 60.68 | 41.74 ± 4.70 | 18.94 ± 2.43 | 1.34 ± 2.51 | - | 0.03 | 18.00 | 0.91 | 0.00 | 0.00 | - | 3504.00 |
| Fixed (1) [Unfiltered] | - | - | - | - | - | - | - | - | 54.95 | 38.01 ± 6.38 | 16.94 ± 4.54 | 4.12 ± 7.16 | 7.38 ± 6.38 | 0.11 | - | 0.00 | 0.00 | 0.00 | - | 0.00 |
| Fixed (1) [Filtered] | - | - | - | - | - | - | - | - | 59.37 | 42.07 ± 5.06 | 17.30 ± 4.18 | 4.45 ± 7.26 | 7.74 ± 6.43 | 0.11 | - | 0.00 | 0.00 | 0.00 | - | 0.00 |
| Nop [Unfiltered] | - | - | - | - | - | - | - | - | 53.25 | 43.25 ± 6.13 | 10.01 ± 5.78 | 19.01 ± 11.71 | - | 0.49 | - | 0.00 | 0.00 | 0.00 | - | 0.00 |
| Projection [Unfiltered] | - | - | - | - | - | - | - | - | 53.60 | 36.42 ± 11.39 | 17.18 ± 5.43 | 0.17 ± 0.24 | - | 0.01 | - | 0.00 | 0.00 | 0.00 | - | 34524.00 |
| Nop [Filtered] | - | - | - | - | - | - | - | - | 53.23 | 43.23 ± 6.13 | 10.00 ± 5.78 | 19.02 ± 11.71 | - | 0.49 | - | 0.00 | 0.00 | 0.00 | - | 0.00 |
| Projection [Filtered] | - | - | - | - | - | - | - | - | 57.23 | 39.30 ± 8.45 | 17.93 ± 4.32 | 1.43 ± 3.66 | - | 0.04 | - | 0.00 | 0.00 | 0.00 | - | 37293.00 |

## 3L30V 3L60V Detailed Metrics

For each metric, the mean and standard error between experiments are given in the format "mean ± SE". 

**Supervisor Statistics:**
- Mean Iterations to Converge: Average number of iterations for the root-finding algorithm to converge
- Convergence Rate: Fraction of root-finding attempts that successfully converged
- Outcome Counts: Number of times each policy augmentation outcome occurred


### Main Experimental Results

| Method | Speed Violations (hr^-1) | Tailgating Violations (hr^-1) | Braking Violations (hr^-1) | LaneKeeping Violations (hr^-1) | Lane Change Tailgating Violations (hr^-1) | Lane Change Braking Violations (hr^-1) | Collision Violations (hr^-1) | Lane Change Collision Violations (hr^-1) | Total Reward | Basic Reward | Added Reward | Total Norm Cost | Expected Norm Cost | Cost Rate | Mean Iterations to Converge | Convergence Rate | Unchanged Count | Naively Augmented Count | SCPS Augmented Count | Projection Count |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Right_Lane Profile** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Adaptive (0.05) [Filtered] | - | - | - | - | - | - | - | - | 51.71 | 36.70 ± 10.08 | 15.01 ± 6.56 | 6.66 ± 9.51 | 9.10 ± 9.28 | 0.18 | 18.00 | 1.00 | 0.00 | 0.00 | - | 124.00 |
| Nop [Unfiltered] | - | - | - | - | - | - | - | - | 5.44 | 4.46 ± 2.01 | 0.98 ± 0.95 | 2.51 ± 2.21 | 2.43 ± 2.10 | 0.56 | - | 0.00 | 0.00 | 0.00 | - | 0.00 |

## 3L30V 4L40V Detailed Metrics

For each metric, the mean and standard error between experiments are given in the format "mean ± SE". 

**Supervisor Statistics:**
- Mean Iterations to Converge: Average number of iterations for the root-finding algorithm to converge
- Convergence Rate: Fraction of root-finding attempts that successfully converged
- Outcome Counts: Number of times each policy augmentation outcome occurred


### Main Experimental Results

| Method | Speed Violations (hr^-1) | Tailgating Violations (hr^-1) | Braking Violations (hr^-1) | LaneKeeping Violations (hr^-1) | Lane Change Tailgating Violations (hr^-1) | Lane Change Braking Violations (hr^-1) | Collision Violations (hr^-1) | Lane Change Collision Violations (hr^-1) | Total Reward | Basic Reward | Added Reward | Total Norm Cost | Expected Norm Cost | Cost Rate | Mean Iterations to Converge | Convergence Rate | Unchanged Count | Naively Augmented Count | SCPS Augmented Count | Projection Count |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Right_Lane Profile** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Adaptive (0.05) [Unfiltered] | - | - | - | - | - | - | - | - | 59.73 | 41.05 ± 5.88 | 18.69 ± 2.89 | 1.22 ± 2.43 | 5.16 ± 2.72 | 0.03 | 18.00 | 1.00 | 0.00 | 0.00 | - | 2938.00 |
| Adaptive (0.05) [Filtered] | - | - | - | - | - | - | - | - | 56.58 | 39.26 ± 4.82 | 17.32 ± 3.88 | 4.63 ± 6.43 | 7.54 ± 6.30 | 0.12 | 18.00 | 1.00 | 0.00 | 0.00 | - | 4485.00 |
| Fixed (1) [Unfiltered] | - | - | - | - | - | - | - | - | 54.81 | 39.03 ± 5.13 | 15.78 ± 5.78 | 7.47 ± 10.73 | 10.09 ± 9.86 | 0.19 | - | 0.00 | 0.00 | 0.00 | - | 0.00 |
| Fixed (1) [Filtered] | - | - | - | - | - | - | - | - | 55.39 | 39.47 ± 3.91 | 15.91 ± 5.64 | 7.65 ± 10.91 | 10.29 ± 10.01 | 0.19 | - | 0.00 | 0.00 | 0.00 | - | 0.00 |
| Nop [Unfiltered] | - | - | - | - | - | - | - | - | 46.95 | 38.10 ± 7.08 | 8.85 ± 5.34 | 20.40 ± 11.11 | 20.51 ± 10.70 | 0.54 | - | 0.00 | 0.00 | 0.00 | - | 0.00 |

## 3L30V 6L60V Detailed Metrics

For each metric, the mean and standard error between experiments are given in the format "mean ± SE". 

**Supervisor Statistics:**
- Mean Iterations to Converge: Average number of iterations for the root-finding algorithm to converge
- Convergence Rate: Fraction of root-finding attempts that successfully converged
- Outcome Counts: Number of times each policy augmentation outcome occurred


### Main Experimental Results

| Method | Speed Violations (hr^-1) | Tailgating Violations (hr^-1) | Braking Violations (hr^-1) | LaneKeeping Violations (hr^-1) | Lane Change Tailgating Violations (hr^-1) | Lane Change Braking Violations (hr^-1) | Collision Violations (hr^-1) | Lane Change Collision Violations (hr^-1) | Total Reward | Basic Reward | Added Reward | Total Norm Cost | Expected Norm Cost | Cost Rate | Mean Iterations to Converge | Convergence Rate | Unchanged Count | Naively Augmented Count | SCPS Augmented Count | Projection Count |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Right_Lane Profile** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Nop [Unfiltered] | - | - | - | - | - | - | - | - | 52.54 | 42.67 ± 7.38 | 9.87 ± 5.63 | 18.80 ± 11.42 | 18.79 ± 9.80 | 0.49 | - | 0.00 | 0.00 | 0.00 | - | 0.00 |

## 4L20V 4L20V Detailed Metrics

For each metric, the mean and standard error between experiments are given in the format "mean ± SE". 

**Supervisor Statistics:**
- Mean Iterations to Converge: Average number of iterations for the root-finding algorithm to converge
- Convergence Rate: Fraction of root-finding attempts that successfully converged
- Outcome Counts: Number of times each policy augmentation outcome occurred


### Main Experimental Results

| Method | Speed Violations (hr^-1) | Tailgating Violations (hr^-1) | Braking Violations (hr^-1) | LaneKeeping Violations (hr^-1) | Lane Change Tailgating Violations (hr^-1) | Lane Change Braking Violations (hr^-1) | Collision Violations (hr^-1) | Lane Change Collision Violations (hr^-1) | Total Reward | Basic Reward | Added Reward | Total Norm Cost | Expected Norm Cost | Cost Rate | Mean Iterations to Converge | Convergence Rate | Unchanged Count | Naively Augmented Count | SCPS Augmented Count | Projection Count |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Cautious Profile** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Unsupervised | 0.98 | 0.02 | 0.11 | 0.55 | 0.04 | 0.03 | 0.01 | 0.01 | 9.74 | - | - | 44.69 ± 13.96 | - | 1.72 | - | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
