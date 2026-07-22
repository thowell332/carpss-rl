# Experiment Results Summary

## 3L30V 3L30V Results


### Main Experimental Results

| Method | Success Rate (%) | Total Reward | Basic Reward | Added Reward | Total Norm Cost | Expected Norm Cost | Normalised Lane Index |
|---|---|---|---|---|---|---|---|
| **Right_Lane Profile** |  |  |  |  |  |  |  |
| Naive [Unfiltered] | 91.80 | 58.14 | 41.87 ± 6.24 | 16.27 ± 5.16 | 5.57 ± 9.19 | 8.62 ± 7.96 | 0.84 ± 0.24 |
| Naive [Filtered] | 95.70 | 59.00 | 42.53 ± 5.19 | 16.47 ± 5.02 | 5.81 ± 9.20 | 8.87 ± 7.94 | 0.84 ± 0.24 |
| Adaptive (0.05) [Unfiltered] | 90.20 | 59.08 | 40.85 ± 6.73 | 18.23 ± 3.27 | 1.27 ± 2.49 | 5.23 ± 2.81 | 0.95 ± 0.08 |
| Adaptive (0.0316) [Filtered] | 96.90 | 60.79 | 42.32 ± 4.25 | 18.47 ± 2.51 | 2.02 ± 3.42 | 5.96 ± 3.52 | 0.94 ± 0.10 |
| Adaptive (0.05) [Filtered] | 95.20 | 60.41 | 41.81 ± 5.11 | 18.60 ± 2.59 | 1.44 ± 2.57 | 5.47 ± 2.85 | 0.95 ± 0.08 |
| Adaptive (0.3162) [Filtered] | 88.20 | 58.29 | 40.05 ± 8.11 | 18.24 ± 3.84 | 0.72 ± 1.37 | 4.75 ± 2.03 | 0.96 ± 0.07 |
| Adaptive (3.1623) [Filtered] | 86.50 | 57.66 | 39.60 ± 8.84 | 18.06 ± 4.21 | 0.67 ± 1.28 | 4.65 ± 1.92 | 0.96 ± 0.08 |
| Adaptive (10) [Filtered] | 84.40 | 57.06 | 39.30 ± 9.01 | 17.76 ± 4.38 | 1.06 ± 2.33 | 4.94 ± 2.66 | 0.95 ± 0.10 |
| Fixed (1) [Unfiltered] | 86.90 | 57.49 | 41.04 ± 7.08 | 16.45 ± 4.88 | 4.50 ± 8.06 | 7.72 ± 7.08 | 0.87 ± 0.21 |
| Fixed (1) [Filtered] | 94.00 | 59.02 | 42.22 ± 5.49 | 16.79 ± 4.61 | 4.95 ± 8.15 | 8.19 ± 7.12 | 0.86 ± 0.22 |
| Nop [Unfiltered] | 95.70 | 53.22 | 43.59 ± 5.80 | 9.63 ± 5.93 | 19.82 ± 12.14 | 19.70 ± 10.34 | 0.49 ± 0.30 |
| Projection [Unfiltered] | 73.00 | 53.50 | 36.63 ± 11.31 | 16.87 ± 5.41 | 0.16 ± 0.23 | 3.93 ± 1.29 | 0.97 ± 0.08 |
| Nop [Filtered] | 95.70 | 53.22 | 43.59 ± 5.80 | 9.63 ± 5.93 | 19.82 ± 12.14 | 19.70 ± 10.34 | 0.49 ± 0.30 |
| Projection [Filtered] | 85.10 | 56.87 | 39.27 ± 8.98 | 17.60 ± 4.50 | 1.40 ± 3.50 | 5.23 ± 3.60 | 0.94 ± 0.11 |

## Experiment Summary

| Profile | Model-Environment | Method | Experiments | Total Episodes |
|---------|-------------------|--------|-------------|----------------|
| Right_Lane | 3L30V 3L30V | Adaptive (0.0316) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (0.05) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (0.3162) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (3.1623) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (10) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (0.05) [Unfiltered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Fixed (1) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Fixed (1) [Unfiltered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Naive [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Naive [Unfiltered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Nop [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Nop [Unfiltered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Projection [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Projection [Unfiltered] | 1 | 1000 |
