# Submission Version Log

## v1

- Generated draft with literature sweep and one synthetic micro-slip diagnostic.
- Reported latent policy MSE 0.01543 versus fixed threshold policy MSE 0.02772.

## v2

- Added tuned baseline stress with constant hold, tuned threshold, raw tactile linear, and EMA tactile linear controllers.
- Found the central evidence failure: tuned EMA tactile reaches 0.00021 on the matched generator and constant hold reaches 0.00058 under tactile bias and friction confounding.
- Reframed the old manuscript as a negative control.

## v3

- Added `scripts/run_full_scale_micro_slip_suite.py`.
- Generated 518,400 compact condition rows representing 171,694,080,000 evaluations and 13,735,526,400,000 frame decisions.
- Evaluated 8 protocols across task, object, sensor, phase, excitation, and shift factors.
- Rewrote the manuscript as "Excitation-Aware Micro-Slip State Estimation for Dexterous Manipulation".
- Built the final 25-page canonical PDF at `C:/Users/wangz/Downloads/53.pdf`.
- Final SHA256: `20EA1D8D3CF3DEF2C46920EF74A971C6C7677F01633211930DEBCA2775141BB7`.
