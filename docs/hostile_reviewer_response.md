# Hostile Reviewer Response

The strongest reviewer objection to the old paper was correct: the original result compared a naive latent filter against weak baselines on a near-constant synthetic target.

The final v3 paper answers that objection by:

- preserving the v2 tuned-baseline collapse as a negative control,
- adding constant, threshold, raw tactile, EMA tactile, friction proxy, old latent, excitation-aware, and oracle protocols,
- expanding to 518,400 compact rows representing 13,735,526,400,000 frame decisions,
- reporting excitation, phase, object, task, and observation-shift stress,
- stating that real tactile logs remain future work.

The final claim is narrower and more defensible: excitation-aware micro-slip state estimation is the best non-oracle protocol in the deterministic benchmark, not a proven real-robot deployment method.
