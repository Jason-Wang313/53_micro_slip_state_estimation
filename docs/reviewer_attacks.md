# Reviewer Attacks

## Attack: The old threshold baseline was weak.

Sustained historically. The final paper keeps the v2 failure and adds tuned threshold, raw tactile, EMA tactile, constant hold, friction proxy, old latent, excitation-aware, and oracle protocols.

## Attack: The controller target was nearly constant.

Sustained historically. The final v3 benchmark includes low-excitation holds as controls and dynamic regimes where target variation makes late intervention costly.

## Attack: The latent filter was not robust to observation shift.

Sustained historically. The final paper keeps the old latent filter as a baseline and adds gain shift, bias shift, friction confounding, and stale tactile streams.

## Attack: The method wins by abstaining.

Addressed. Update abstention is reported; excitation-aware abstention is 0.132359, while observability recall, excitation coverage, late intervention, dropped contact, and control MSE are also reported.

## Attack: This is not real robot evidence.

Sustained as a limitation. The paper explicitly claims a deterministic benchmark and reporting discipline, not hardware deployment safety.
