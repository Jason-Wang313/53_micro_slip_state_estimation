# Novelty Boundary Map

## Not Novel

- Generic slip detection.
- Binary incipient-slip classification.
- Friction estimation.
- Tactile smoothing before control.
- Grasp stabilization as a broad topic.

## Historical Collapse

The original synthetic experiment did not show that a latent micro-slip estimator was necessary. Tuned EMA tactile and constant hold defeated the naive latent filter in the v2 hardening pass.

## Final Novelty Boundary

The final contribution is an excitation-aware benchmark and estimator/reporting discipline for continuous micro-slip state estimation. The paper's novelty is the conditional claim: state estimation helps when contact is observable, dynamically excited, and control-relevant, and this must be reported against tuned continuous baselines and observation shifts.

## Not Claimed

- Real tactile-log validation.
- Hardware deployment safety.
- Universal dominance in low-excitation stable holds.
- A final solution to tactile slip estimation.
