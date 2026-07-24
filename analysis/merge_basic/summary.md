# Experiment Results Summary

## MERGE_BASIC MERGE_BASIC Results


### Main Experimental Results

| Method | Success Rate (%) | Total Reward | Basic Reward | Added Reward | Total Norm Cost | Expected Norm Cost | Normalised Lane Index | Mean Courtesy Gap Violation |
|---|---|---|---|---|---|---|---|---|
| **Merge_Courtesy Profile** |  |  |  |  |  |  |  |  |
| Naive [Unfiltered] | 99.60 | 16.03 | 17.56 ± 0.52 | -1.53 ± 1.53 | 1.94 ± 1.91 | 1.91 ± 1.38 | 0.74 ± 0.31 | 6.55 ± 6.50 |
| Naive [Filtered] | 99.60 | 16.03 | 17.56 ± 0.52 | -1.53 ± 1.53 | 1.94 ± 1.91 | 1.91 ± 1.38 | 0.74 ± 0.31 | 6.55 ± 6.50 |
| Adaptive (0.05) [Unfiltered] | 99.10 | 17.08 | 17.08 ± 0.50 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.31 ± 0.25 | 0.00 ± 0.03 |
| Adaptive (0.005) [Filtered] | 99.10 | 14.83 | 18.25 ± 0.81 | -3.41 ± 1.64 | 3.41 ± 2.02 | 3.41 ± 1.27 | 0.67 ± 0.30 | 31.33 ± 8.10 |
| Adaptive (0.01) [Filtered] | 99.20 | 16.22 | 17.37 ± 0.62 | -1.15 ± 0.89 | 0.77 ± 0.91 | 1.91 ± 0.68 | 0.28 ± 0.20 | 19.96 ± 8.53 |
| Adaptive (0.02) [Filtered] | 99.20 | 16.70 | 17.10 ± 0.53 | -0.39 ± 0.10 | 0.00 ± 0.01 | 1.42 ± 0.32 | 0.17 ± 0.15 | 14.80 ± 6.87 |
| Adaptive (0.025) [Filtered] | 99.30 | 17.08 | 17.08 ± 0.50 | -0.00 ± 0.02 | 0.00 ± 0.01 | 0.74 ± 0.37 | 0.31 ± 0.25 | 0.00 ± 0.03 |
| Adaptive (0.03) [Filtered] | 99.20 | 16.70 | 17.10 ± 0.53 | -0.39 ± 0.10 | 0.00 ± 0.00 | 1.42 ± 0.32 | 0.17 ± 0.15 | 14.79 ± 6.87 |
| Adaptive (0.0316) [Filtered] | 99.30 | 17.08 | 17.08 ± 0.50 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.31 ± 0.25 | 0.00 ± 0.03 |
| Adaptive (0.05) [Filtered] | 99.30 | 17.08 | 17.08 ± 0.50 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.31 ± 0.25 | 0.00 ± 0.03 |
| Adaptive (0.3162) [Filtered] | 99.30 | 17.08 | 17.08 ± 0.49 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.31 ± 0.25 | 0.00 ± 0.03 |
| Adaptive (3.1623) [Filtered] | 99.30 | 17.08 | 17.08 ± 0.49 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.31 ± 0.25 | 0.00 ± 0.03 |
| Adaptive (10) [Filtered] | 99.30 | 17.08 | 17.08 ± 0.49 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.31 ± 0.25 | 0.00 ± 0.03 |
| Fixed (1) [Unfiltered] | 99.40 | 16.44 | 17.36 ± 0.54 | -0.92 ± 1.31 | 1.13 ± 1.63 | 1.45 ± 1.18 | 0.56 ± 0.32 | 4.07 ± 5.54 |
| Fixed (1) [Filtered] | 99.40 | 16.44 | 17.36 ± 0.54 | -0.92 ± 1.31 | 1.13 ± 1.63 | 1.45 ± 1.18 | 0.56 ± 0.32 | 4.07 ± 5.54 |
| Nop [Unfiltered] | 99.40 | 14.08 | 18.91 ± 0.44 | -4.83 ± 1.50 | 5.29 ± 1.57 | 4.36 ± 1.33 | 0.98 ± 0.04 | 36.52 ± 9.73 |
| Projection [Unfiltered] | 99.10 | 17.07 | 17.08 ± 0.50 | -0.00 ± 0.02 | 0.00 ± 0.00 | 0.74 ± 0.37 | 0.31 ± 0.25 | 0.00 ± 0.03 |
| Nop [Filtered] | 99.60 | 15.36 | 17.84 ± 0.38 | -2.48 ± 1.60 | 3.23 ± 1.85 | 2.60 ± 1.54 | 0.98 ± 0.04 | 10.24 ± 7.10 |
| Projection [Filtered] | 99.20 | 16.70 | 17.10 ± 0.53 | -0.39 ± 0.10 | 0.00 ± 0.00 | 1.42 ± 0.32 | 0.17 ± 0.15 | 14.79 ± 6.87 |

## Experiment Summary

| Profile | Model-Environment | Method | Experiments | Total Episodes |
|---------|-------------------|--------|-------------|----------------|
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Adaptive (0.005) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Adaptive (0.01) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Adaptive (0.02) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Adaptive (0.025) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Adaptive (0.03) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Adaptive (0.0316) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Adaptive (0.05) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Adaptive (0.3162) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Adaptive (3.1623) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Adaptive (10) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Adaptive (0.05) [Unfiltered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Fixed (1) [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Fixed (1) [Unfiltered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Naive [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Naive [Unfiltered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Nop [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Nop [Unfiltered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Projection [Filtered] | 1 | 1000 |
| Merge_Courtesy | MERGE_BASIC MERGE_BASIC | Projection [Unfiltered] | 1 | 1000 |
