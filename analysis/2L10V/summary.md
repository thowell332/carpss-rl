# Experiment Results Summary

## 4L20V 2L10V Results


### Main Experimental Results

| Method | Success Rate (%) | Collision Rate (hr^-1) | Cost Rate (hr^-1) | Speed (m/s) |
|---|---|---|---|---|
| **Cautious Profile** |  |  |  |  |
| Unsupervised | 0.40 | 494.70 ± 1.40 | 7590.12 ± 54.83 | 29.16 ± 0.03 |
| Filter_Only | 3.20 | 397.72 ± 3.23 | 7525.75 ± 53.41 | 29.24 ± 0.02 |
| Naive | 19.80 | 178.62 ± 3.97 | 2797.10 ± 80.92 | 25.38 ± 0.05 |
| Adaptive (0.01) | 29.40 | 142.66 ± 4.12 | 2422.90 ± 57.67 | 24.57 ± 0.03 |
| Adaptive (0.1) | 73.80 | 35.91 ± 2.70 | 1329.13 ± 12.34 | 22.54 ± 0.02 |
| Adaptive (1) | 80.00 | 26.35 ± 2.36 | 602.85 ± 27.48 | 21.96 ± 0.04 |
| Fixed (0.01) | 80.00 | 26.35 ± 2.36 | 602.85 ± 27.48 | 21.96 ± 0.04 |
| Fixed (0.1) | 82.40 | 22.92 ± 2.22 | 688.32 ± 27.78 | 22.02 ± 0.05 |
| Fixed (1) | 37.80 | 117.28 ± 4.09 | 2382.02 ± 50.51 | 24.47 ± 0.03 |
| Projection | 80.00 | 26.35 ± 2.36 | 602.85 ± 27.48 | 21.96 ± 0.04 |
|  |  |  |  |  |
| **Efficient Profile** |  |  |  |  |
| Unsupervised | 0.40 | 494.70 ± 1.40 | 3756.07 ± 38.11 | 29.16 ± 0.03 |
| Filter_Only | 3.20 | 397.72 ± 3.23 | 3340.39 ± 43.80 | 29.24 ± 0.02 |
| Naive | 5.80 | 338.71 ± 3.76 | 2674.80 ± 39.95 | 29.08 ± 0.01 |
| Adaptive (0.01) | 9.60 | 288.41 ± 4.20 | 2234.30 ± 40.21 | 28.21 ± 0.07 |
| Adaptive (0.1) | 32.20 | 145.60 ± 4.49 | 1553.56 ± 37.44 | 26.08 ± 0.09 |
| Adaptive (1) | 58.40 | 66.65 ± 3.53 | 757.07 ± 47.00 | 23.86 ± 0.06 |
| Fixed (0.01) | 59.40 | 64.69 ± 3.50 | 687.57 ± 34.91 | 23.73 ± 0.06 |
| Fixed (0.1) | 55.40 | 73.53 ± 3.66 | 947.48 ± 56.93 | 24.37 ± 0.08 |
| Fixed (1) | 9.40 | 289.77 ± 4.17 | 2421.88 ± 22.25 | 28.35 ± 0.11 |
| Projection | 59.40 | 64.69 ± 3.50 | 687.57 ± 34.91 | 23.73 ± 0.06 |

### Ablation Studies

| Method | Success Rate (%) | Collision Rate (hr^-1) | Cost Rate (hr^-1) | Speed (m/s) |
|---|---|---|---|---|
| **Cautious Profile** |  |  |  |  |
| Naive | 10.40 | 239.50 ± 3.65 | 2414.70 ± 74.16 | 25.17 ± 0.02 |
| Adaptive (0.01) | 11.80 | 228.83 ± 3.74 | 2206.67 ± 57.88 | 25.00 ± 0.00 |
| Adaptive (0.1) | 67.60 | 46.68 ± 3.02 | 1292.59 ± 18.10 | 22.58 ± 0.01 |
| Adaptive (1) | 65.20 | 50.55 ± 3.09 | 457.52 ± 24.71 | 22.04 ± 0.04 |
| Fixed (0.01) | 65.20 | 50.55 ± 3.09 | 457.52 ± 24.71 | 22.04 ± 0.04 |
| Fixed (0.1) | 79.00 | 28.18 ± 2.44 | 659.07 ± 30.63 | 22.04 ± 0.05 |
| Fixed (1) | 11.60 | 229.88 ± 3.72 | 2218.96 ± 60.80 | 25.00 ± 0.00 |
| Projection | 65.20 | 50.55 ± 3.09 | 457.52 ± 24.71 | 22.04 ± 0.04 |
|  |  |  |  |  |
| **Efficient Profile** |  |  |  |  |
| Naive | 4.80 | 367.33 ± 3.69 | 2804.25 ± 45.70 | 29.17 ± 0.02 |
| Adaptive (0.01) | 5.00 | 352.43 ± 3.62 | 2497.10 ± 28.73 | 28.87 ± 0.04 |
| Adaptive (0.1) | 30.00 | 157.95 ± 4.62 | 1525.49 ± 32.49 | 26.16 ± 0.09 |
| Adaptive (1) | 54.20 | 76.89 ± 3.74 | 617.74 ± 41.59 | 23.81 ± 0.08 |
| Fixed (0.01) | 53.20 | 80.12 ± 3.82 | 483.45 ± 11.23 | 23.49 ± 0.05 |
| Fixed (0.1) | 50.60 | 86.22 ± 3.90 | 1057.82 ± 36.58 | 24.74 ± 0.10 |
| Fixed (1) | 5.40 | 346.87 ± 3.71 | 2687.97 ± 44.13 | 29.11 ± 0.04 |
| Projection | 53.20 | 80.12 ± 3.82 | 483.45 ± 11.23 | 23.49 ± 0.05 |

## Experiment Summary

| Profile | Model-Environment | Method | Experiments | Total Episodes |
|---------|-------------------|--------|-------------|----------------|
| Efficient | 4L20V 2L10V | Unsupervised | 5 | 500 |
| Efficient | 4L20V 2L10V | Projection | 5 | 500 |
| Efficient | 4L20V 2L10V | Naive | 5 | 500 |
| Efficient | 4L20V 2L10V | Fixed (1) | 5 | 500 |
| Efficient | 4L20V 2L10V | Fixed (0.1) | 5 | 500 |
| Efficient | 4L20V 2L10V | Fixed (0.01) | 5 | 500 |
| Efficient | 4L20V 2L10V | Filter_Only | 5 | 500 |
| Efficient | 4L20V 2L10V | Adaptive (1) | 5 | 500 |
| Efficient | 4L20V 2L10V | Adaptive (0.1) | 5 | 500 |
| Efficient | 4L20V 2L10V | Adaptive (0.01) | 5 | 500 |
| Cautious | 4L20V 2L10V | Unsupervised | 5 | 500 |
| Cautious | 4L20V 2L10V | Projection | 5 | 500 |
| Cautious | 4L20V 2L10V | Naive | 5 | 500 |
| Cautious | 4L20V 2L10V | Fixed (1) | 5 | 500 |
| Cautious | 4L20V 2L10V | Fixed (0.1) | 5 | 500 |
| Cautious | 4L20V 2L10V | Fixed (0.01) | 5 | 500 |
| Cautious | 4L20V 2L10V | Filter_Only | 5 | 500 |
| Cautious | 4L20V 2L10V | Adaptive (1) | 5 | 500 |
| Cautious | 4L20V 2L10V | Adaptive (0.1) | 5 | 500 |
| Cautious | 4L20V 2L10V | Adaptive (0.01) | 5 | 500 |

## Ablation Studies

| Profile | Model-Environment | Method | Experiments | Total Episodes |
|---------|-------------------|--------|-------------|----------------|
| Efficient | 4L20V 2L10V | Projection | 5 | 500 |
| Efficient | 4L20V 2L10V | Naive | 5 | 500 |
| Efficient | 4L20V 2L10V | Fixed (1) | 5 | 500 |
| Efficient | 4L20V 2L10V | Fixed (0.1) | 5 | 500 |
| Efficient | 4L20V 2L10V | Fixed (0.01) | 5 | 500 |
| Efficient | 4L20V 2L10V | Adaptive (1) | 5 | 500 |
| Efficient | 4L20V 2L10V | Adaptive (0.1) | 5 | 500 |
| Efficient | 4L20V 2L10V | Adaptive (0.01) | 5 | 500 |
| Cautious | 4L20V 2L10V | Projection | 5 | 500 |
| Cautious | 4L20V 2L10V | Naive | 5 | 500 |
| Cautious | 4L20V 2L10V | Fixed (1) | 5 | 500 |
| Cautious | 4L20V 2L10V | Fixed (0.1) | 5 | 500 |
| Cautious | 4L20V 2L10V | Fixed (0.01) | 5 | 500 |
| Cautious | 4L20V 2L10V | Adaptive (1) | 5 | 500 |
| Cautious | 4L20V 2L10V | Adaptive (0.1) | 5 | 500 |
| Cautious | 4L20V 2L10V | Adaptive (0.01) | 5 | 500 |
