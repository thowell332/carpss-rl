# Detailed Experimental Metrics

## MERGE_BASIC MERGE_BASIC Detailed Metrics

For each metric, cells are **mean ± sample standard deviation** over episodes (`ddof=1`), in the format "mean ± std".

- **Mean Iterations to Converge**: Average number of iterations for the root-finding algorithm to converge
- **Convergence Rate**: Fraction of root-finding attempts that successfully converged
- **Outcome Fractions**: Fraction of decision steps with each policy augmentation outcome


### Main Experimental Results

| Method | Mean Iterations to Converge | Convergence Rate | Unchanged Fraction | Naively Augmented Fraction | SCPS Augmented Fraction | Projection Fraction |
|---|---|---|---|---|---|---|
| **Merge_Courtesy Profile** |  |  |  |  |  |  |
| Naive [Unfiltered] | - | 0.00 | 0.39 | 0.61 | 0.00 | 0.00 |
| Naive [Filtered] | - | 0.00 | 0.39 | 0.61 | 0.00 | 0.00 |
| Adaptive (0.05) [Unfiltered] | 18.00 | 1.00 | 0.40 | 0.00 | 0.60 | 0.00 |
| Adaptive (0.05) [Filtered] | 18.00 | 1.00 | 0.40 | 0.00 | 0.60 | 0.00 |
| Fixed (0.5) [Unfiltered] | - | 0.00 | 0.40 | 0.00 | 0.60 | 0.00 |
| Fixed (0.75) [Unfiltered] | - | 0.00 | 0.40 | 0.00 | 0.60 | 0.00 |
| Fixed (1) [Unfiltered] | - | 0.00 | 0.39 | 0.00 | 0.61 | 0.00 |
| Fixed (5) [Unfiltered] | - | 0.00 | 0.39 | 0.00 | 0.61 | 0.00 |
| Fixed (10) [Unfiltered] | - | 0.00 | 0.39 | 0.00 | 0.61 | 0.00 |
| Fixed (0.1) [Filtered] | - | 0.00 | 0.40 | 0.00 | 0.60 | 0.00 |
| Fixed (0.5) [Filtered] | - | 0.00 | 0.40 | 0.00 | 0.60 | 0.00 |
| Fixed (0.75) [Filtered] | - | 0.00 | 0.40 | 0.00 | 0.60 | 0.00 |
| Fixed (1) [Filtered] | - | 0.00 | 0.39 | 0.00 | 0.61 | 0.00 |
| Fixed (5) [Filtered] | - | 0.00 | 0.39 | 0.00 | 0.61 | 0.00 |
| Fixed (10) [Filtered] | - | 0.00 | 0.39 | 0.00 | 0.61 | 0.00 |
| Nop [Unfiltered] | - | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Projection [Unfiltered] | - | 0.00 | 0.40 | 0.00 | 0.00 | 0.60 |
| Nop [Filtered] | - | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| Projection [Filtered] | - | 0.00 | 0.40 | 0.00 | 0.00 | 0.60 |
|  |  |  |  |  |  |  |
| **Right_Lane Profile** |  |  |  |  |  |  |
| Adaptive (0.01) [Filtered] | 18.00 | 1.00 | 0.00 | 0.00 | 0.99 | 0.01 |
| Adaptive (0.0316) [Filtered] | 18.00 | 1.00 | 0.00 | 0.00 | 0.99 | 0.01 |
| Adaptive (0.1) [Filtered] | 18.00 | 1.00 | 0.00 | 0.00 | 0.99 | 0.01 |
| Adaptive (0.3162) [Filtered] | 18.00 | 0.04 | 0.00 | 0.00 | 0.00 | 1.00 |
| Adaptive (1) [Filtered] | 18.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| Adaptive (3.1623) [Filtered] | 18.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| Adaptive (10) [Filtered] | - | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| Adaptive (31.623) [Filtered] | - | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| Adaptive (100) [Filtered] | - | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
