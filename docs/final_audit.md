# Final Audit

Paper-readiness judgment: kill/archive.

## Original Thesis

Micro-slip should be estimated as a continuous control-relevant latent state rather than only detected as a binary slip event.

## Hardest Reviewer Attack

The synthetic target action is nearly solved by constant or lightly calibrated tactile control. The manuscript compares the latent filter to a weak fixed threshold that overreacts by construction.

## V2 Stress Evidence

- Matched generator: latent filter MSE 0.01453; tuned EMA tactile MSE 0.00021.
- Matched generator: tuned threshold MSE 0.00040, far below the original fixed-threshold MSE 0.02772.
- Low tactile gain: latent filter MSE 0.01240; tuned EMA tactile MSE 0.00034.
- Tactile bias shift: latent filter MSE 0.06434; constant hold MSE 0.00058.
- Friction confound: latent filter MSE 0.05102; constant hold MSE 0.00058.
- Noisy tactile: latent filter MSE 0.01789; tuned EMA tactile MSE 0.00036.

## Decision

Kill/archive. The core synthetic result collapses under tuned baselines. The repo should not be submitted as a positive micro-slip estimator paper.

## Recovery Requirements

- Real tactile or proprioceptive grasp logs.
- A control target not nearly solved by constant hold.
- Tuned threshold, raw tactile, EMA tactile, friction proxy, and simple state-estimator baselines.
- Calibration-shift and object-family holdout tests.
- Multiple seeds, uncertainty, and failure-case reporting.

## Artifact Policy

- Canonical PDF: `C:/Users/wangz/Downloads/53.pdf`
- Local tracked/generated PDF policy: `paper/main.pdf` is ignored and removed after build.
- Desktop copy: absent.
