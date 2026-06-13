# Claims

## Rejected Submission Claims

- Reject: the current latent filter is better evidence for micro-slip state estimation than tuned tactile baselines.
- Reject: the synthetic diagnostic supports an algorithmic advantage.
- Reject: the paper is ready for archival submission.

## Surviving Claim

- Micro-slip as a continuous control state remains a plausible research question.
- The current repo provides a negative baseline lesson: constant, threshold, raw tactile, and EMA tactile baselines must be tuned before claiming a latent-state advantage.

## Evidence Boundary

V2 hardening shows the original evidence collapses. On the matched generator, the latent filter MSE is 0.01453 while the tuned EMA tactile baseline is 0.00021. Under tactile bias and friction confounding, constant hold stays at 0.00058 while the latent filter rises to 0.06434 and 0.05102.
