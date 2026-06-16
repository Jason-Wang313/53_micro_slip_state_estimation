# Experiment Rigor Checklist

- Full-factor benchmark: yes, 12 tasks, 6 object/contact families, 5 sensor suites, 6 contact phases, 6 excitation regimes, 5 observation shifts, and 8 protocols.
- RAM-light execution: yes, streamed compact rows and summary accumulators.
- Strong baselines: yes, constant hold, tuned threshold, raw tactile, EMA tactile, friction proxy, old latent, and oracle.
- Calibration stress: yes, gain shift, bias shift, friction confounding, and noisy/stale tactile streams.
- Dynamic stress: yes, burst shear, rolling contact, regrasp transition, and recovery after partial slip.
- Negative control: yes, v2 tuned-baseline collapse is preserved in the manuscript.
- Uncertainty/error bars: deterministic aggregate benchmark; represented repetition counts are recorded.
- Real robot data: no, explicitly stated as future work.
- Decision: final v3 full-scale submission artifact.
