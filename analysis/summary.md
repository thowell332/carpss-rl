# Experiment Results Summary

## 3L30V 3L30V Results


### Main Experimental Results

| Method | Success Rate (%) | Total Reward | Basic Reward | Added Reward | Total Norm Cost | Expected Norm Cost | Normalised Lane Index |
|---|---|---|---|---|---|---|---|
| **Right_Lane Profile** |  |  |  |  |  |  |  |
| Naive [Unfiltered] | 92.40 | 55.03 | 38.60 ± 5.45 | 16.43 ± 5.14 | 5.75 ± 9.36 | 8.75 ± 8.12 | 0.84 ± 0.24 |
| Naive [Filtered] | 95.80 | 55.73 | 39.14 ± 4.52 | 16.59 ± 5.01 | 5.95 ± 9.38 | 8.97 ± 8.10 | 0.84 ± 0.24 |
| Adaptive (0.05) [Unfiltered] | 89.70 | 56.51 | 38.10 ± 6.41 | 18.40 ± 3.36 | 1.30 ± 2.60 | 5.23 ± 2.93 | 0.95 ± 0.08 |
| Adaptive (0.0316) [Filtered] | 96.60 | 57.95 | 39.33 ± 3.95 | 18.62 ± 2.60 | 2.10 ± 3.63 | 6.00 ± 3.73 | 0.93 ± 0.10 |
| Adaptive (0.05) [Filtered] | 94.60 | 57.72 | 38.96 ± 4.96 | 18.75 ± 2.74 | 1.46 ± 2.67 | 5.45 ± 2.98 | 0.95 ± 0.08 |
| Adaptive (0.3162) [Filtered] | 87.30 | 55.72 | 37.39 ± 7.90 | 18.33 ± 3.97 | 0.72 ± 1.50 | 4.69 ± 2.13 | 0.96 ± 0.07 |
| Adaptive (3.1623) [Filtered] | 85.80 | 55.28 | 37.08 ± 8.42 | 18.21 ± 4.22 | 0.66 ± 1.25 | 4.59 ± 1.95 | 0.96 ± 0.08 |
| Adaptive (10) [Filtered] | 83.90 | 54.75 | 36.84 ± 8.59 | 17.90 ± 4.38 | 1.03 ± 2.24 | 4.87 ± 2.62 | 0.95 ± 0.09 |
| Fixed (1) [Unfiltered] | 86.50 | 54.14 | 37.63 ± 6.81 | 16.51 ± 4.96 | 4.62 ± 8.22 | 7.77 ± 7.24 | 0.87 ± 0.22 |
| Fixed (1) [Filtered] | 93.40 | 55.61 | 38.76 ± 5.22 | 16.85 ± 4.67 | 5.05 ± 8.34 | 8.23 ± 7.30 | 0.86 ± 0.22 |
| Nop [Unfiltered] | 96.40 | 48.78 | 39.20 ± 4.44 | 9.57 ± 5.91 | 20.06 ± 12.08 | 19.91 ± 10.29 | 0.49 ± 0.30 |
| Projection [Unfiltered] | 72.50 | 51.21 | 34.20 ± 10.92 | 17.02 ± 5.47 | 0.17 ± 0.24 | 3.88 ± 1.30 | 0.97 ± 0.08 |
| Nop [Filtered] | 96.40 | 48.78 | 39.20 ± 4.44 | 9.57 ± 5.91 | 20.06 ± 12.08 | 19.91 ± 10.29 | 0.49 ± 0.30 |
| Projection [Filtered] | 84.00 | 54.46 | 36.75 ± 8.69 | 17.71 ± 4.53 | 1.33 ± 3.22 | 5.11 ± 3.39 | 0.94 ± 0.11 |

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
