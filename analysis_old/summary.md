# Experiment Results Summary

## 3L30V 3L30V Results


### Main Experimental Results

| Method | Success Rate (%) | Total Reward | Basic Reward | Added Reward | Total Norm Cost | Expected Norm Cost | Normalised Lane Index |
|---|---|---|---|---|---|---|---|
| **Right_Lane Profile** |  |  |  |  |  |  |  |
| Naive [Unfiltered] | 91.40 | 58.47 | 41.75 ± 5.98 | 16.72 ± 4.65 | 5.21 ± 8.18 | - | 0.85 ± 0.22 |
| Naive [Filtered] | 95.40 | 59.35 | 42.44 ± 4.67 | 16.90 ± 4.51 | 5.45 ± 8.26 | - | 0.85 ± 0.22 |
| Adaptive (0.05) [Unfiltered] | 91.00 | 59.60 | 40.96 ± 6.11 | 18.64 ± 3.00 | 1.21 ± 2.43 | - | 0.95 ± 0.07 |
| Adaptive (0.05) [Filtered] | 95.30 | 60.68 | 41.74 ± 4.70 | 18.94 ± 2.43 | 1.34 ± 2.51 | - | 0.95 ± 0.07 |
| Fixed (1) [Unfiltered] | 88.00 | 54.95 | 38.01 ± 6.38 | 16.94 ± 4.54 | 4.12 ± 7.16 | 7.38 ± 6.38 | 0.88 ± 0.20 |
| Fixed (1) [Filtered] | 94.00 | 59.37 | 42.07 ± 5.06 | 17.30 ± 4.18 | 4.45 ± 7.26 | 7.74 ± 6.43 | 0.87 ± 0.20 |
| Nop [Unfiltered] | 95.70 | 53.25 | 43.25 ± 6.13 | 10.01 ± 5.78 | 19.01 ± 11.71 | - | 0.51 ± 0.29 |
| Projection [Unfiltered] | 74.90 | 53.60 | 36.42 ± 11.39 | 17.18 ± 5.43 | 0.17 ± 0.24 | - | 0.96 ± 0.08 |
| Nop [Filtered] | 95.60 | 53.23 | 43.23 ± 6.13 | 10.00 ± 5.78 | 19.02 ± 11.71 | - | 0.51 ± 0.29 |
| Projection [Filtered] | 86.70 | 57.23 | 39.30 ± 8.45 | 17.93 ± 4.32 | 1.43 ± 3.66 | - | 0.94 ± 0.11 |

## 3L30V 3L60V Results


### Main Experimental Results

| Method | Success Rate (%) | Total Reward | Basic Reward | Added Reward | Total Norm Cost | Expected Norm Cost | Normalised Lane Index |
|---|---|---|---|---|---|---|---|
| **Right_Lane Profile** |  |  |  |  |  |  |  |
| Adaptive (0.05) [Filtered] | 90.00 | 51.71 | 36.70 ± 10.08 | 15.01 ± 6.56 | 6.66 ± 9.51 | 9.10 ± 9.28 | 0.17 ± 0.13 |
| Nop [Unfiltered] | 0.00 | 5.44 | 4.46 ± 2.01 | 0.98 ± 0.95 | 2.51 ± 2.21 | 2.43 ± 2.10 | 0.46 ± 0.36 |

## 3L30V 4L40V Results


### Main Experimental Results

| Method | Success Rate (%) | Total Reward | Basic Reward | Added Reward | Total Norm Cost | Expected Norm Cost | Normalised Lane Index |
|---|---|---|---|---|---|---|---|
| **Right_Lane Profile** |  |  |  |  |  |  |  |
| Adaptive (0.05) [Unfiltered] | 91.63 | 59.73 | 41.05 ± 5.88 | 18.69 ± 2.89 | 1.22 ± 2.43 | 5.16 ± 2.72 | 0.95 ± 0.07 |
| Adaptive (0.05) [Filtered] | 97.50 | 56.58 | 39.26 ± 4.82 | 17.32 ± 3.88 | 4.63 ± 6.43 | 7.54 ± 6.30 | 0.86 ± 0.17 |
| Fixed (1) [Unfiltered] | 96.00 | 54.81 | 39.03 ± 5.13 | 15.78 ± 5.78 | 7.47 ± 10.73 | 10.09 ± 9.86 | 0.79 ± 0.28 |
| Fixed (1) [Filtered] | 97.90 | 55.39 | 39.47 ± 3.91 | 15.91 ± 5.64 | 7.65 ± 10.91 | 10.29 ± 10.01 | 0.79 ± 0.28 |
| Nop [Unfiltered] | 92.10 | 46.95 | 38.10 ± 7.08 | 8.85 ± 5.34 | 20.40 ± 11.11 | 20.51 ± 10.70 | 0.47 ± 0.27 |

## 3L30V 6L60V Results


### Main Experimental Results

| Method | Success Rate (%) | Total Reward | Basic Reward | Added Reward | Total Norm Cost | Expected Norm Cost | Normalised Lane Index |
|---|---|---|---|---|---|---|---|
| **Right_Lane Profile** |  |  |  |  |  |  |  |
| Nop [Unfiltered] | 94.49 | 52.54 | 42.67 ± 7.38 | 9.87 ± 5.63 | 18.80 ± 11.42 | 18.79 ± 9.80 | 0.21 ± 0.11 |

## 4L20V 4L20V Results


### Main Experimental Results

| Method | Success Rate (%) | Total Reward | Basic Reward | Added Reward | Total Norm Cost | Expected Norm Cost | Normalised Lane Index |
|---|---|---|---|---|---|---|---|
| **Cautious Profile** |  |  |  |  |  |  |  |
| Unsupervised | 71.30 | 9.74 | - | - | 44.69 ± 13.96 | - | 0.46 ± 0.23 |

## Experiment Summary

| Profile | Model-Environment | Method | Experiments | Total Episodes |
|---------|-------------------|--------|-------------|----------------|
| Cautious | 4L20V 4L20V | Unsupervised | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (0.05) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (0.05) [Unfiltered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Fixed (1) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Fixed (1) [Unfiltered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Naive [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Naive [Unfiltered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Nop [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Nop [Unfiltered] | 1 | 999 |
| Right_Lane | 3L30V 3L30V | Projection [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Projection [Unfiltered] | 1 | 1000 |
| Right_Lane | 3L30V 3L60V | Adaptive (0.05) [Filtered] | 1 | 30 |
| Right_Lane | 3L30V 3L60V | Nop [Unfiltered] | 1 | 132 |
| Right_Lane | 3L30V 4L40V | Adaptive (0.05) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 4L40V | Adaptive (0.05) [Unfiltered] | 1 | 848 |
| Right_Lane | 3L30V 4L40V | Fixed (1) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 4L40V | Fixed (1) [Unfiltered] | 1 | 1000 |
| Right_Lane | 3L30V 4L40V | Nop [Unfiltered] | 1 | 1000 |
| Right_Lane | 3L30V 6L60V | Nop [Unfiltered] | 1 | 127 |
