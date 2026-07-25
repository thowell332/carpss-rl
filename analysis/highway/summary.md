# Experiment Results Summary

## 3L30V 3L30V Results


### Main Experimental Results

| Method | Success Rate (%) | Total Reward | Basic Reward | Added Reward | Total Norm Cost | Expected Norm Cost | Normalised Lane Index |
|---|---|---|---|---|---|---|---|
| **Right_Lane Profile** |  |  |  |  |  |  |  |
| Naive [Unfiltered] | 91.80 | 58.14 ± 9.37 | 41.87 ± 6.24 | 16.27 ± 5.16 | 5.57 ± 9.19 | 8.62 ± 7.96 | 0.84 ± 0.24 |
| Naive [Filtered] | 95.70 | 59.00 ± 8.12 | 42.53 ± 5.19 | 16.47 ± 5.02 | 5.81 ± 9.20 | 8.87 ± 7.94 | 0.84 ± 0.24 |
| Adaptive (0.05) [Unfiltered] | 90.20 | 59.08 ± 9.71 | 40.85 ± 6.73 | 18.23 ± 3.27 | 1.27 ± 2.49 | 5.23 ± 2.81 | 0.95 ± 0.08 |
| Adaptive (1e-05) [Filtered] | 97.04 | 53.71 ± 8.46 | 43.87 ± 5.26 | 9.84 ± 5.95 | 19.63 ± 12.09 | 19.61 ± 10.25 | 0.50 ± 0.30 |
| Adaptive (3.16e-05) [Filtered] | 97.00 | 54.03 ± 8.41 | 43.82 ± 5.19 | 10.21 ± 5.93 | 18.87 ± 12.01 | 19.00 ± 10.20 | 0.52 ± 0.30 |
| Adaptive (0.0001) [Filtered] | 97.10 | 54.44 ± 8.32 | 43.77 ± 5.09 | 10.66 ± 5.91 | 17.95 ± 11.90 | 18.28 ± 10.10 | 0.54 ± 0.29 |
| Adaptive (0.000316) [Filtered] | 97.20 | 55.02 ± 8.21 | 43.77 ± 5.01 | 11.25 ± 5.87 | 16.76 ± 11.78 | 17.38 ± 10.00 | 0.57 ± 0.29 |
| Adaptive (0.001) [Filtered] | 97.50 | 56.29 ± 7.96 | 43.77 ± 4.96 | 12.52 ± 5.62 | 14.18 ± 11.16 | 15.38 ± 9.53 | 0.63 ± 0.28 |
| Adaptive (0.0032) [Filtered] | 97.00 | 57.99 ± 7.80 | 43.57 ± 5.14 | 14.42 ± 5.03 | 10.19 ± 9.61 | 12.30 ± 8.31 | 0.73 ± 0.24 |
| Adaptive (0.01) [Filtered] | 97.60 | 60.11 ± 6.62 | 43.24 ± 4.52 | 16.87 ± 3.87 | 5.30 ± 6.85 | 8.53 ± 6.23 | 0.85 ± 0.18 |
| Adaptive (0.0316) [Filtered] | 96.90 | 60.79 ± 6.06 | 42.32 ± 4.25 | 18.47 ± 2.51 | 2.02 ± 3.42 | 5.96 ± 3.52 | 0.94 ± 0.10 |
| Adaptive (0.05) [Filtered] | 95.20 | 60.41 ± 7.31 | 41.81 ± 5.11 | 18.60 ± 2.59 | 1.44 ± 2.57 | 5.47 ± 2.85 | 0.95 ± 0.08 |
| Adaptive (0.1) [Filtered] | 92.40 | 59.69 ± 8.93 | 41.14 ± 6.16 | 18.54 ± 2.99 | 1.07 ± 2.19 | 5.15 ± 2.64 | 0.96 ± 0.07 |
| Adaptive (0.3162) [Filtered] | 88.20 | 58.29 ± 11.86 | 40.05 ± 8.11 | 18.24 ± 3.84 | 0.72 ± 1.37 | 4.75 ± 2.03 | 0.96 ± 0.07 |
| Adaptive (1) [Filtered] | 87.00 | 57.78 ± 12.83 | 39.68 ± 8.74 | 18.11 ± 4.16 | 0.64 ± 1.20 | 4.64 ± 1.92 | 0.96 ± 0.08 |
| Adaptive (3.1623) [Filtered] | 86.80 | 57.78 ± 12.81 | 39.67 ± 8.73 | 18.11 ± 4.15 | 0.62 ± 1.18 | 4.62 ± 1.88 | 0.96 ± 0.08 |
| Adaptive (10) [Filtered] | 86.70 | 57.77 ± 12.81 | 39.66 ± 8.73 | 18.11 ± 4.15 | 0.62 ± 1.18 | 4.62 ± 1.88 | 0.96 ± 0.08 |
| Adaptive (31.623) [Filtered] | 86.70 | 57.77 ± 12.81 | 39.66 ± 8.73 | 18.11 ± 4.15 | 0.62 ± 1.18 | 4.62 ± 1.88 | 0.96 ± 0.08 |
| Adaptive (100) [Filtered] | 86.70 | 57.77 ± 12.81 | 39.66 ± 8.73 | 18.11 ± 4.15 | 0.62 ± 1.18 | 4.62 ± 1.88 | 0.96 ± 0.08 |
| Fixed (0.75) [Unfiltered] | 82.90 | 56.68 ± 11.65 | 40.15 ± 8.07 | 16.52 ± 4.88 | 3.58 ± 7.22 | 6.94 ± 6.41 | 0.89 ± 0.20 |
| Fixed (1) [Unfiltered] | 86.90 | 57.49 ± 10.33 | 41.04 ± 7.08 | 16.45 ± 4.88 | 4.50 ± 8.06 | 7.72 ± 7.08 | 0.87 ± 0.21 |
| Fixed (0.5) [Filtered] | 90.70 | 58.81 ± 9.36 | 41.37 ± 6.48 | 17.44 ± 4.01 | 3.03 ± 5.80 | 6.66 ± 5.31 | 0.91 ± 0.16 |
| Fixed (0.75) [Filtered] | 92.70 | 58.99 ± 8.74 | 41.89 ± 5.94 | 17.09 ± 4.38 | 4.09 ± 7.30 | 7.51 ± 6.46 | 0.88 ± 0.20 |
| Fixed (1) [Filtered] | 94.00 | 59.02 ± 8.28 | 42.22 ± 5.49 | 16.79 ± 4.61 | 4.95 ± 8.15 | 8.19 ± 7.12 | 0.86 ± 0.22 |
| Nop [Unfiltered] | 95.70 | 53.22 ± 8.93 | 43.59 ± 5.80 | 9.63 ± 5.93 | 19.82 ± 12.14 | 19.70 ± 10.34 | 0.49 ± 0.30 |
| Projection [Unfiltered] | 73.00 | 53.50 ± 16.70 | 36.63 ± 11.31 | 16.87 ± 5.41 | 0.16 ± 0.23 | 3.93 ± 1.29 | 0.97 ± 0.08 |
| Nop [Filtered] | 95.70 | 53.22 ± 8.93 | 43.59 ± 5.80 | 9.63 ± 5.93 | 19.82 ± 12.14 | 19.70 ± 10.34 | 0.49 ± 0.30 |
| Projection [Filtered] | 86.70 | 57.77 ± 12.81 | 39.66 ± 8.73 | 18.11 ± 4.15 | 0.62 ± 1.18 | 4.62 ± 1.88 | 0.96 ± 0.08 |

## Experiment Summary

| Profile | Model-Environment | Method | Experiments | Total Episodes |
|---------|-------------------|--------|-------------|----------------|
| Right_Lane | 3L30V 3L30V | Adaptive (1e-05) [Filtered] | 1 | 743 |
| Right_Lane | 3L30V 3L30V | Adaptive (3.16e-05) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (0.0001) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (0.000316) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (0.001) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (0.0032) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (0.01) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (0.0316) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (0.05) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (0.1) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (0.3162) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (1) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (3.1623) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (10) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (31.623) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (100) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Adaptive (0.05) [Unfiltered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Fixed (0.5) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Fixed (0.75) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Fixed (1) [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Fixed (0.75) [Unfiltered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Fixed (1) [Unfiltered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Naive [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Naive [Unfiltered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Nop [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Nop [Unfiltered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Projection [Filtered] | 1 | 1000 |
| Right_Lane | 3L30V 3L30V | Projection [Unfiltered] | 1 | 1000 |
