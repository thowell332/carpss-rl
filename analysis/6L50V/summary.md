# Experiment Results Summary

## 4L20V 6L50V Results


### Main Experimental Results

| Method | Success Rate (%) | Collision Rate (hr^-1) | Cost Rate (hr^-1) | Speed (m/s) |
|---|---|---|---|---|
| **Cautious Profile** |  |  |  |  |
| Unsupervised | 43.60 | 93.95 ± 3.69 | 6359.96 ± 59.91 | 28.92 ± 0.06 |
| Filter_Only | 61.60 | 56.64 ± 3.21 | 6186.17 ± 69.87 | 28.74 ± 0.07 |
| Naive | 88.60 | 14.49 ± 1.81 | 2872.51 ± 105.47 | 25.81 ± 0.12 |
| Adaptive (0.01) | 96.60 | 4.13 ± 0.99 | 2042.01 ± 50.24 | 24.59 ± 0.02 |
| Adaptive (0.1) | 99.00 | 1.20 ± 0.54 | 1146.03 ± 76.85 | 24.18 ± 0.04 |
| Adaptive (1) | 99.20 | 0.96 ± 0.48 | 872.19 ± 81.56 | 24.00 ± 0.05 |
| Fixed (0.01) | 99.20 | 0.96 ± 0.48 | 862.09 ± 77.11 | 24.01 ± 0.05 |
| Fixed (0.1) | 99.20 | 0.96 ± 0.48 | 876.29 ± 81.93 | 24.00 ± 0.05 |
| Fixed (1) | 92.00 | 9.94 ± 1.51 | 2281.46 ± 61.08 | 25.16 ± 0.07 |
| Projection | 99.20 | 0.96 ± 0.48 | 862.09 ± 77.11 | 24.01 ± 0.05 |
|  |  |  |  |  |
| **Efficient Profile** |  |  |  |  |
| Unsupervised | 43.60 | 93.95 ± 3.69 | 1619.61 ± 63.85 | 28.92 ± 0.06 |
| Filter_Only | 61.60 | 56.64 ± 3.21 | 1481.11 ± 69.66 | 28.74 ± 0.07 |
| Naive | 75.20 | 33.73 ± 2.63 | 856.88 ± 36.03 | 28.26 ± 0.11 |
| Adaptive (0.01) | 79.00 | 27.93 ± 2.42 | 836.75 ± 46.98 | 28.17 ± 0.13 |
| Adaptive (0.1) | 95.40 | 5.66 ± 1.15 | 474.62 ± 27.75 | 27.46 ± 0.12 |
| Adaptive (1) | 96.80 | 3.92 ± 0.96 | 375.12 ± 23.87 | 27.23 ± 0.11 |
| Fixed (0.01) | 96.80 | 3.92 ± 0.96 | 372.92 ± 23.33 | 27.22 ± 0.10 |
| Fixed (0.1) | 97.00 | 3.67 ± 0.93 | 373.29 ± 22.09 | 27.22 ± 0.10 |
| Fixed (1) | 82.40 | 22.97 ± 2.22 | 713.74 ± 37.15 | 28.07 ± 0.12 |
| Projection | 96.80 | 3.92 ± 0.96 | 372.92 ± 23.33 | 27.22 ± 0.10 |

### Ablation Studies

| Method | Success Rate (%) | Collision Rate (hr^-1) | Cost Rate (hr^-1) | Speed (m/s) |
|---|---|---|---|---|
| **Cautious Profile** |  |  |  |  |
| Naive | 77.40 | 30.32 ± 2.51 | 2904.47 ± 104.56 | 25.85 ± 0.12 |
| Adaptive (0.01) | 89.80 | 12.78 ± 1.70 | 2066.85 ± 48.39 | 24.63 ± 0.02 |
| Adaptive (0.1) | 97.00 | 3.64 ± 0.93 | 1165.92 ± 79.53 | 24.20 ± 0.03 |
| Adaptive (1) | 99.20 | 0.96 ± 0.48 | 872.19 ± 81.56 | 24.00 ± 0.05 |
| Fixed (0.01) | 99.20 | 0.96 ± 0.48 | 862.09 ± 77.11 | 24.01 ± 0.05 |
| Fixed (1) | 81.00 | 24.87 ± 2.30 | 2547.70 ± 47.88 | 25.41 ± 0.05 |
| Projection | 99.20 | 0.96 ± 0.48 | 862.09 ± 77.11 | 24.01 ± 0.05 |
|  |  |  |  |  |
| **Efficient Profile** |  |  |  |  |
| Naive | 60.40 | 58.49 ± 3.23 | 919.91 ± 40.67 | 28.34 ± 0.11 |
| Adaptive (0.01) | 61.80 | 55.39 ± 3.15 | 907.81 ± 39.59 | 28.30 ± 0.14 |
| Adaptive (0.1) | 91.20 | 11.01 ± 1.59 | 481.19 ± 24.53 | 27.44 ± 0.12 |
| Adaptive (1) | 95.80 | 5.17 ± 1.10 | 358.51 ± 18.23 | 27.16 ± 0.10 |
| Fixed (0.01) | 95.80 | 5.17 ± 1.10 | 357.77 ± 18.54 | 27.16 ± 0.10 |
| Fixed (0.1) | 95.80 | 5.17 ± 1.10 | 363.02 ± 20.68 | 27.17 ± 0.09 |
| Fixed (1) | 64.00 | 51.98 ± 3.10 | 868.83 ± 32.42 | 28.25 ± 0.11 |
| Projection | 95.80 | 5.17 ± 1.10 | 357.77 ± 18.54 | 27.16 ± 0.10 |

## Experiment Summary

| Profile | Model-Environment | Method | Experiments | Total Episodes |
|---------|-------------------|--------|-------------|----------------|
| Efficient | 4L20V 6L50V | Unsupervised | 5 | 500 |
| Efficient | 4L20V 6L50V | Projection | 5 | 500 |
| Efficient | 4L20V 6L50V | Naive | 5 | 500 |
| Efficient | 4L20V 6L50V | Fixed (1) | 5 | 500 |
| Efficient | 4L20V 6L50V | Fixed (0.1) | 5 | 500 |
| Efficient | 4L20V 6L50V | Fixed (0.01) | 5 | 500 |
| Efficient | 4L20V 6L50V | Filter_Only | 5 | 500 |
| Efficient | 4L20V 6L50V | Adaptive (1) | 5 | 500 |
| Efficient | 4L20V 6L50V | Adaptive (0.1) | 5 | 500 |
| Efficient | 4L20V 6L50V | Adaptive (0.01) | 5 | 500 |
| Cautious | 4L20V 6L50V | Unsupervised | 5 | 500 |
| Cautious | 4L20V 6L50V | Projection | 5 | 500 |
| Cautious | 4L20V 6L50V | Naive | 5 | 500 |
| Cautious | 4L20V 6L50V | Fixed (1) | 5 | 500 |
| Cautious | 4L20V 6L50V | Fixed (0.1) | 5 | 500 |
| Cautious | 4L20V 6L50V | Fixed (0.01) | 5 | 500 |
| Cautious | 4L20V 6L50V | Filter_Only | 5 | 500 |
| Cautious | 4L20V 6L50V | Adaptive (1) | 5 | 500 |
| Cautious | 4L20V 6L50V | Adaptive (0.1) | 5 | 500 |
| Cautious | 4L20V 6L50V | Adaptive (0.01) | 5 | 500 |

## Ablation Studies

| Profile | Model-Environment | Method | Experiments | Total Episodes |
|---------|-------------------|--------|-------------|----------------|
| Efficient | 4L20V 6L50V | Projection | 5 | 500 |
| Efficient | 4L20V 6L50V | Naive | 5 | 500 |
| Efficient | 4L20V 6L50V | Fixed (1) | 5 | 500 |
| Efficient | 4L20V 6L50V | Fixed (0.1) | 5 | 500 |
| Efficient | 4L20V 6L50V | Fixed (0.01) | 5 | 500 |
| Efficient | 4L20V 6L50V | Adaptive (1) | 5 | 500 |
| Efficient | 4L20V 6L50V | Adaptive (0.1) | 5 | 500 |
| Efficient | 4L20V 6L50V | Adaptive (0.01) | 5 | 500 |
| Cautious | 4L20V 6L50V | Projection | 5 | 500 |
| Cautious | 4L20V 6L50V | Naive | 5 | 500 |
| Cautious | 4L20V 6L50V | Fixed (1) | 5 | 500 |
| Cautious | 4L20V 6L50V | Fixed (0.01) | 5 | 500 |
| Cautious | 4L20V 6L50V | Adaptive (1) | 5 | 500 |
| Cautious | 4L20V 6L50V | Adaptive (0.1) | 5 | 500 |
| Cautious | 4L20V 6L50V | Adaptive (0.01) | 5 | 500 |
