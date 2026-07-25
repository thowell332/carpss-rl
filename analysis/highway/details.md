# Detailed Experimental Metrics

## 3L30V 3L30V Detailed Metrics

For each metric, cells are **mean ± sample standard deviation** over episodes (`ddof=1`), in the format "mean ± std".

- **Mean Iterations to Converge**: Average number of iterations for the root-finding algorithm to converge
- **Convergence Rate**: Fraction of root-finding attempts that successfully converged
- **Outcome Fractions**: Fraction of decision steps with each policy augmentation outcome


### Main Experimental Results

| Method | Mean Iterations to Converge | Convergence Rate | Unchanged Fraction | Naively Augmented Fraction | SCPS Augmented Fraction | Projection Fraction |
|---|---|---|---|---|---|---|
| **Right_Lane Profile** |  |  |  |  |  |  |
| Naive [Unfiltered] | - | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| Naive [Filtered] | - | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| Adaptive (0.05) [Unfiltered] | 18.00 | 1.00 | 0.00 | 0.00 | 0.92 | 0.08 |
| Adaptive (1e-05) [Filtered] | 18.00 | 1.00 | 0.00 | 0.00 | 0.99 | 0.01 |
| Adaptive (3.16e-05) [Filtered] | 18.00 | 1.00 | 0.00 | 0.00 | 0.99 | 0.01 |
| Adaptive (0.0001) [Filtered] | 18.00 | 1.00 | 0.00 | 0.00 | 0.98 | 0.02 |
| Adaptive (0.000316) [Filtered] | 18.00 | 1.00 | 0.00 | 0.00 | 0.98 | 0.02 |
| Adaptive (0.001) [Filtered] | 18.00 | 1.00 | 0.00 | 0.00 | 0.97 | 0.03 |
| Adaptive (0.0032) [Filtered] | 18.00 | 1.00 | 0.00 | 0.00 | 0.96 | 0.04 |
| Adaptive (0.01) [Filtered] | 18.00 | 1.00 | 0.00 | 0.00 | 0.95 | 0.05 |
| Adaptive (0.0316) [Filtered] | 18.00 | 1.00 | 0.00 | 0.00 | 0.93 | 0.07 |
| Adaptive (0.05) [Filtered] | 18.00 | 1.00 | 0.00 | 0.00 | 0.92 | 0.08 |
| Adaptive (0.1) [Filtered] | 18.00 | 1.00 | 0.00 | 0.00 | 0.89 | 0.11 |
| Adaptive (0.3162) [Filtered] | 18.00 | 0.91 | 0.00 | 0.00 | 0.18 | 0.82 |
| Adaptive (1) [Filtered] | 17.99 | 0.73 | 0.00 | 0.00 | 0.05 | 0.95 |
| Adaptive (3.1623) [Filtered] | 18.00 | 0.17 | 0.00 | 0.00 | 0.02 | 0.98 |
| Adaptive (10) [Filtered] | 17.99 | 0.11 | 0.00 | 0.00 | 0.01 | 0.99 |
| Adaptive (31.623) [Filtered] | - | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| Adaptive (100) [Filtered] | - | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| Fixed (0.75) [Unfiltered] | - | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| Fixed (1) [Unfiltered] | - | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| Fixed (0.5) [Filtered] | - | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| Fixed (0.75) [Filtered] | - | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| Fixed (1) [Filtered] | - | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| Nop [Unfiltered] | - | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Projection [Unfiltered] | - | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
| Nop [Filtered] | - | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| Projection [Filtered] | - | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
