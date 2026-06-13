# Reviewer Attacks

## Attack: The threshold baseline is weak by construction.

Sustained. A tuned threshold gets 0.00040 MSE on the matched generator, far below the manuscript's fixed-threshold 0.02772 and below the latent filter's 0.01453.

## Attack: The controller target is nearly constant.

Sustained. Constant hold reaches 0.00058 MSE and beats the latent filter in every v2 scenario.

## Attack: The latent filter is not robust to observation shift.

Sustained. Under tactile bias shift, latent filter MSE rises to 0.06434 while constant hold remains 0.00058. Under friction confounding, latent filter MSE is 0.05102.

## Attack: This is not enough evidence for a submission.

Sustained. Decision: kill/archive.
