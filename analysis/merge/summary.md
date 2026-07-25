# Experiment Results Summary

## MERGE_BASIC MERGE_BASIC Results


### Main Experimental Results

| Method | Success Rate (%) | Total Reward | Basic Reward | Added Reward | Total Norm Cost | Expected Norm Cost | Normalised Lane Index | Mean Courtesy Gap Violation (full ep.) |
|---|---|---|---|---|---|---|---|---|
| **Merge_Courtesy Profile** |  |  |  |  |  |  |  |  |
| Naive [Unfiltered] | 99.80 | 13.72 ± 1.63 | 17.62 ± 0.49 | -3.90 ± 1.72 | 4.07 ± 2.07 | 3.74 ± 1.37 | 0.79 ± 0.29 | 18.40 ± 10.76 |
| Naive [Filtered] | 99.80 | 13.72 ± 1.63 | 17.62 ± 0.49 | -3.90 ± 1.72 | 4.07 ± 2.07 | 3.74 ± 1.37 | 0.79 ± 0.29 | 18.40 ± 10.76 |
| Adaptive (0.05) [Unfiltered] | 99.00 | 16.51 ± 0.46 | 16.90 ± 0.43 | -0.39 ± 0.10 | 0.00 ± 0.00 | 1.42 ± 0.32 | 0.17 ± 0.15 | 1.20 ± 0.57 |
| Adaptive (0.05) [Filtered] | 99.20 | 16.51 ± 0.46 | 16.91 ± 0.43 | -0.39 ± 0.10 | 0.00 ± 0.00 | 1.42 ± 0.32 | 0.17 ± 0.15 | 1.20 ± 0.57 |
| Fixed (0.5) [Unfiltered] | 99.00 | 16.51 ± 0.46 | 16.90 ± 0.43 | -0.39 ± 0.10 | 0.00 ± 0.00 | 1.42 ± 0.32 | 0.17 ± 0.15 | 1.20 ± 0.57 |
| Fixed (0.75) [Unfiltered] | 98.90 | 15.62 ± 0.98 | 17.09 ± 0.48 | -1.47 ± 1.02 | 1.10 ± 1.04 | 2.12 ± 0.76 | 0.32 ± 0.21 | 5.80 ± 4.87 |
| Fixed (1) [Unfiltered] | 99.50 | 14.14 ± 1.50 | 17.48 ± 0.52 | -3.34 ± 1.65 | 3.31 ± 2.03 | 3.36 ± 1.26 | 0.66 ± 0.31 | 15.19 ± 9.76 |
| Fixed (5) [Unfiltered] | 99.40 | 13.01 ± 1.64 | 17.83 ± 0.39 | -4.83 ± 1.50 | 5.29 ± 1.57 | 4.36 ± 1.33 | 0.98 ± 0.04 | 23.72 ± 10.65 |
| Fixed (10) [Unfiltered] | 99.40 | 13.01 ± 1.64 | 17.84 ± 0.39 | -4.83 ± 1.50 | 5.29 ± 1.57 | 4.36 ± 1.33 | 0.98 ± 0.04 | 23.71 ± 10.65 |
| Fixed (0.1) [Filtered] | 99.20 | 16.51 ± 0.46 | 16.91 ± 0.43 | -0.39 ± 0.10 | 0.00 ± 0.00 | 1.42 ± 0.32 | 0.17 ± 0.15 | 1.20 ± 0.57 |
| Fixed (0.5) [Filtered] | 99.20 | 16.51 ± 0.46 | 16.91 ± 0.43 | -0.39 ± 0.10 | 0.00 ± 0.00 | 1.42 ± 0.32 | 0.17 ± 0.15 | 1.20 ± 0.57 |
| Fixed (0.75) [Filtered] | 99.10 | 15.63 ± 0.98 | 17.10 ± 0.48 | -1.47 ± 1.02 | 1.10 ± 1.04 | 2.12 ± 0.76 | 0.32 ± 0.21 | 5.80 ± 4.87 |
| Fixed (1) [Filtered] | 99.50 | 14.14 ± 1.50 | 17.48 ± 0.52 | -3.34 ± 1.65 | 3.31 ± 2.03 | 3.36 ± 1.26 | 0.66 ± 0.31 | 15.19 ± 9.76 |
| Fixed (5) [Filtered] | 99.60 | 13.01 ± 1.64 | 17.84 ± 0.38 | -4.83 ± 1.50 | 5.29 ± 1.57 | 4.36 ± 1.33 | 0.98 ± 0.04 | 23.71 ± 10.64 |
| Fixed (10) [Filtered] | 99.60 | 13.01 ± 1.64 | 17.84 ± 0.38 | -4.83 ± 1.50 | 5.29 ± 1.57 | 4.36 ± 1.33 | 0.98 ± 0.04 | 23.70 ± 10.65 |
| Nop [Unfiltered] | 99.40 | 13.01 ± 1.64 | 17.84 ± 0.39 | -4.83 ± 1.50 | 5.29 ± 1.57 | 4.36 ± 1.33 | 0.98 ± 0.04 | 23.71 ± 10.65 |
| Projection [Unfiltered] | 99.00 | 16.51 ± 0.46 | 16.90 ± 0.43 | -0.39 ± 0.10 | 0.00 ± 0.00 | 1.42 ± 0.32 | 0.17 ± 0.15 | 1.20 ± 0.57 |
| Nop [Filtered] | 99.50 | 14.35 ± 1.74 | 18.91 ± 0.55 | -4.56 ± 1.52 | 5.01 ± 1.58 | 4.12 ± 1.34 | 0.99 ± 0.04 | 21.91 ± 10.71 |
| Projection [Filtered] | 99.20 | 16.51 ± 0.46 | 16.91 ± 0.43 | -0.39 ± 0.10 | 0.00 ± 0.00 | 1.42 ± 0.32 | 0.17 ± 0.15 | 1.20 ± 0.57 |
|  |  |  |  |  |  |  |  |  |
| **Right_Lane Profile** |  |  |  |  |  |  |  |  |
| Adaptive (0.01) [Filtered] | 99.70 | 13.01 ± 1.64 | 17.84 ± 0.39 | -4.83 ± 1.50 | 1.59 ± 0.23 | 3.47 ± 0.24 | 1.00 ± 0.01 | 23.70 ± 10.65 |
| Adaptive (0.0316) [Filtered] | 99.70 | 13.01 ± 1.64 | 17.84 ± 0.39 | -4.83 ± 1.50 | 1.59 ± 0.21 | 3.47 ± 0.24 | 1.00 ± 0.00 | 23.70 ± 10.65 |
| Adaptive (0.1) [Filtered] | 99.70 | 13.01 ± 1.64 | 17.84 ± 0.39 | -4.83 ± 1.50 | 1.59 ± 0.21 | 3.47 ± 0.24 | 1.00 ± 0.00 | 23.70 ± 10.65 |
| Adaptive (0.3162) [Filtered] | 99.70 | 13.01 ± 1.64 | 17.84 ± 0.39 | -4.83 ± 1.50 | 1.59 ± 0.21 | 3.47 ± 0.24 | 1.00 ± 0.00 | 23.70 ± 10.65 |
| Adaptive (1) [Filtered] | 99.70 | 13.01 ± 1.64 | 17.84 ± 0.39 | -4.83 ± 1.50 | 1.59 ± 0.21 | 3.47 ± 0.24 | 1.00 ± 0.00 | 23.70 ± 10.65 |
| Adaptive (3.1623) [Filtered] | 99.70 | 13.01 ± 1.64 | 17.84 ± 0.39 | -4.83 ± 1.50 | 1.59 ± 0.21 | 3.47 ± 0.24 | 1.00 ± 0.00 | 23.70 ± 10.65 |
| Adaptive (10) [Filtered] | 99.70 | 13.01 ± 1.64 | 17.84 ± 0.39 | -4.83 ± 1.50 | 1.59 ± 0.21 | 3.47 ± 0.24 | 1.00 ± 0.00 | 23.70 ± 10.65 |
| Adaptive (31.623) [Filtered] | 99.70 | 13.01 ± 1.64 | 17.84 ± 0.39 | -4.83 ± 1.50 | 1.59 ± 0.21 | 3.47 ± 0.24 | 1.00 ± 0.00 | 23.70 ± 10.65 |
| Adaptive (100) [Filtered] | 99.70 | 13.01 ± 1.64 | 17.84 ± 0.39 | -4.83 ± 1.50 | 1.59 ± 0.21 | 3.47 ± 0.24 | 1.00 ± 0.00 | 23.70 ± 10.65 |

## Experiment Summary

| Profile | Model-Environment | Method | Experiments | Total Episodes |
|---------|-------------------|--------|-------------|----------------|
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Adaptive (0.05) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Adaptive (0.05) [Unfiltered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Fixed (0.1) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Fixed (0.5) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Fixed (0.75) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Fixed (1) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Fixed (5) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Fixed (10) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Fixed (0.5) [Unfiltered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Fixed (0.75) [Unfiltered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Fixed (1) [Unfiltered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Fixed (5) [Unfiltered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Fixed (10) [Unfiltered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Naive [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Naive [Unfiltered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Nop [Filtered] | 1 | 201 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Nop [Unfiltered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Projection [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Projection [Unfiltered] | 1 | 1000 |
| Right_Lane | MERGE_BASIC MERGE_BASIC | Adaptive (0.01) [Filtered] | 1 | 1000 |
| Right_Lane | MERGE_BASIC MERGE_BASIC | Adaptive (0.0316) [Filtered] | 1 | 1000 |
| Right_Lane | MERGE_BASIC MERGE_BASIC | Adaptive (0.1) [Filtered] | 1 | 1000 |
| Right_Lane | MERGE_BASIC MERGE_BASIC | Adaptive (0.3162) [Filtered] | 1 | 1000 |
| Right_Lane | MERGE_BASIC MERGE_BASIC | Adaptive (1) [Filtered] | 1 | 1000 |
| Right_Lane | MERGE_BASIC MERGE_BASIC | Adaptive (3.1623) [Filtered] | 1 | 1000 |
| Right_Lane | MERGE_BASIC MERGE_BASIC | Adaptive (10) [Filtered] | 1 | 1000 |
| Right_Lane | MERGE_BASIC MERGE_BASIC | Adaptive (31.623) [Filtered] | 1 | 1000 |
| Right_Lane | MERGE_BASIC MERGE_BASIC | Adaptive (100) [Filtered] | 1 | 1000 |
