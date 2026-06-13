# Submission Attack Log

## Attack: weak fixed threshold

Result: Sustained. Tuned threshold MSE is 0.00040 on the matched generator versus 0.01453 for the latent filter.

Decision impact: central evidence collapse.

## Attack: near-constant target

Result: Sustained. Constant hold MSE is 0.00058 and beats the latent filter in all v2 scenarios.

Decision impact: kill/archive.

## Attack: observation bias and friction confounding

Result: Sustained. Latent filter MSE rises to 0.06434 under tactile bias and 0.05102 under friction confounding.

Decision impact: archive until real data and stronger baselines exist.
