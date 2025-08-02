# Experiment Results Summary

## 4L20V 4L20V Results


### Main Experimental Results

| Method | Success Rate (%) | Collision Rate (hr^-1) | Cost Rate (hr^-1) | Speed (m/s) |
|---|---|---|---|---|
| **Cautious Profile** |  |  |  |  |
| Unsupervised | 75.80 | 33.07 ± 2.62 | 6290.04 ± 21.07 | 29.71 ± 0.01 |
| Filter_Only | 76.80 | 31.54 ± 2.57 | 6236.62 ± 28.87 | 29.67 ± 0.02 |
| Naive | 91.80 | 10.20 ± 1.53 | 2300.61 ± 75.50 | 26.32 ± 0.06 |
| Adaptive (0.01) | 96.60 | 4.14 ± 0.99 | 1143.60 ± 52.67 | 24.95 ± 0.03 |
| Adaptive (0.1) | 99.20 | 0.96 ± 0.48 | 651.37 ± 47.39 | 24.35 ± 0.02 |
| Adaptive (1) | 99.00 | 1.21 ± 0.54 | 443.92 ± 45.34 | 24.03 ± 0.05 |
| Fixed (0.01) | 99.00 | 1.21 ± 0.54 | 443.92 ± 45.34 | 24.03 ± 0.05 |
| Fixed (0.1) | 99.20 | 0.96 ± 0.48 | 443.76 ± 45.21 | 24.02 ± 0.04 |
| Fixed (1) | 94.40 | 6.91 ± 1.27 | 1633.12 ± 68.47 | 25.58 ± 0.05 |
| Projection | 99.00 | 1.21 ± 0.54 | 443.92 ± 45.34 | 24.03 ± 0.05 |
|  |  |  |  |  |
| **Efficient Profile** |  |  |  |  |
| Unsupervised | 75.80 | 33.07 ± 2.62 | 1742.60 ± 23.92 | 29.71 ± 0.01 |
| Filter_Only | 76.80 | 31.54 ± 2.57 | 1699.54 ± 33.83 | 29.67 ± 0.02 |
| Naive | 75.80 | 32.80 ± 2.60 | 764.62 ± 22.00 | 29.24 ± 0.05 |
| Adaptive (0.01) | 81.20 | 24.68 ± 2.29 | 671.71 ± 13.28 | 29.00 ± 0.05 |
| Adaptive (0.1) | 90.60 | 11.98 ± 1.66 | 337.46 ± 37.03 | 27.81 ± 0.07 |
| Adaptive (1) | 91.20 | 11.19 ± 1.61 | 298.46 ± 26.88 | 27.69 ± 0.09 |
| Fixed (0.01) | 91.20 | 11.19 ± 1.61 | 296.94 ± 27.12 | 27.69 ± 0.09 |
| Fixed (0.1) | 91.20 | 11.19 ± 1.61 | 294.48 ± 27.64 | 27.70 ± 0.09 |
| Fixed (1) | 79.60 | 27.26 ± 2.41 | 647.17 ± 20.67 | 28.92 ± 0.04 |
| Projection | 91.20 | 11.19 ± 1.61 | 296.94 ± 27.12 | 27.69 ± 0.09 |

### Ablation Studies

| Method | Success Rate (%) | Collision Rate (hr^-1) | Cost Rate (hr^-1) | Speed (m/s) |
|---|---|---|---|---|
| **Cautious Profile** |  |  |  |  |
| Naive | 90.60 | 11.73 ± 1.63 | 2343.00 ± 83.87 | 26.38 ± 0.06 |
| Adaptive (0.01) | 95.60 | 5.37 ± 1.12 | 1172.12 ± 60.09 | 24.98 ± 0.04 |
| Adaptive (0.1) | 99.20 | 0.96 ± 0.48 | 654.02 ± 48.79 | 24.35 ± 0.02 |
| Adaptive (1) | 99.20 | 0.96 ± 0.48 | 443.52 ± 45.25 | 24.02 ± 0.04 |
| Fixed (0.01) | 99.00 | 1.21 ± 0.54 | 443.92 ± 45.34 | 24.03 ± 0.05 |
| Fixed (0.1) | 99.20 | 0.96 ± 0.48 | 444.00 ± 45.17 | 24.02 ± 0.04 |
| Fixed (1) | 92.60 | 9.16 ± 1.45 | 1824.71 ± 63.88 | 25.82 ± 0.05 |
| Projection | 99.00 | 1.21 ± 0.54 | 443.92 ± 45.34 | 24.03 ± 0.05 |
|  |  |  |  |  |
| **Efficient Profile** |  |  |  |  |
| Naive | 72.60 | 37.43 ± 2.73 | 789.19 ± 13.97 | 29.34 ± 0.04 |
| Adaptive (0.01) | 78.60 | 28.40 ± 2.43 | 694.77 ± 22.07 | 29.14 ± 0.03 |
| Adaptive (0.1) | 89.40 | 13.63 ± 1.77 | 328.92 ± 36.78 | 27.85 ± 0.06 |
| Adaptive (1) | 90.00 | 12.78 ± 1.72 | 266.65 ± 24.97 | 27.59 ± 0.07 |
| Fixed (0.01) | 90.00 | 12.78 ± 1.72 | 265.63 ± 25.26 | 27.59 ± 0.07 |
| Fixed (0.1) | 89.80 | 13.06 ± 1.73 | 265.02 ± 25.97 | 27.62 ± 0.09 |
| Fixed (1) | 74.20 | 34.92 ± 2.65 | 741.08 ± 18.45 | 29.26 ± 0.03 |
| Projection | 90.00 | 12.78 ± 1.72 | 265.63 ± 25.26 | 27.59 ± 0.07 |

## Experiment Summary

| Profile | Model-Environment | Method | Experiments | Total Episodes |
|---------|-------------------|--------|-------------|----------------|
| Efficient | 4L20V 4L20V | Unsupervised | 5 | 500 |
| Efficient | 4L20V 4L20V | Projection | 5 | 500 |
| Efficient | 4L20V 4L20V | Naive | 5 | 500 |
| Efficient | 4L20V 4L20V | Fixed (1) | 5 | 500 |
| Efficient | 4L20V 4L20V | Fixed (0.1) | 5 | 500 |
| Efficient | 4L20V 4L20V | Fixed (0.01) | 5 | 500 |
| Efficient | 4L20V 4L20V | Filter_Only | 5 | 500 |
| Efficient | 4L20V 4L20V | Adaptive (1) | 5 | 500 |
| Efficient | 4L20V 4L20V | Adaptive (0.1) | 5 | 500 |
| Efficient | 4L20V 4L20V | Adaptive (0.01) | 5 | 500 |
| Cautious | 4L20V 4L20V | Unsupervised | 5 | 500 |
| Cautious | 4L20V 4L20V | Projection | 5 | 500 |
| Cautious | 4L20V 4L20V | Naive | 5 | 500 |
| Cautious | 4L20V 4L20V | Fixed (1) | 5 | 500 |
| Cautious | 4L20V 4L20V | Fixed (0.1) | 5 | 500 |
| Cautious | 4L20V 4L20V | Fixed (0.01) | 5 | 500 |
| Cautious | 4L20V 4L20V | Filter_Only | 5 | 500 |
| Cautious | 4L20V 4L20V | Adaptive (1) | 5 | 500 |
| Cautious | 4L20V 4L20V | Adaptive (0.1) | 5 | 500 |
| Cautious | 4L20V 4L20V | Adaptive (0.01) | 5 | 500 |

## Ablation Studies

| Profile | Model-Environment | Method | Experiments | Total Episodes |
|---------|-------------------|--------|-------------|----------------|
| Efficient | 4L20V 4L20V | Projection | 5 | 500 |
| Efficient | 4L20V 4L20V | Naive | 5 | 500 |
| Efficient | 4L20V 4L20V | Fixed (1) | 5 | 500 |
| Efficient | 4L20V 4L20V | Fixed (0.1) | 5 | 500 |
| Efficient | 4L20V 4L20V | Fixed (0.01) | 5 | 500 |
| Efficient | 4L20V 4L20V | Adaptive (1) | 5 | 500 |
| Efficient | 4L20V 4L20V | Adaptive (0.1) | 5 | 500 |
| Efficient | 4L20V 4L20V | Adaptive (0.01) | 5 | 500 |
| Cautious | 4L20V 4L20V | Projection | 5 | 500 |
| Cautious | 4L20V 4L20V | Naive | 5 | 500 |
| Cautious | 4L20V 4L20V | Fixed (1) | 5 | 500 |
| Cautious | 4L20V 4L20V | Fixed (0.1) | 5 | 500 |
| Cautious | 4L20V 4L20V | Fixed (0.01) | 5 | 500 |
| Cautious | 4L20V 4L20V | Adaptive (1) | 5 | 500 |
| Cautious | 4L20V 4L20V | Adaptive (0.1) | 5 | 500 |
| Cautious | 4L20V 4L20V | Adaptive (0.01) | 5 | 500 |
