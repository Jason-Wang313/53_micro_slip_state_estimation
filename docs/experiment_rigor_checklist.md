# Experiment Rigor Checklist

- Multiple held-out seeds: yes, v2 uses train seeds 100-107 and evaluation seeds 200-205.
- Stronger baselines: yes, constant hold, tuned threshold, raw tactile linear, and EMA tactile linear.
- Calibration stress: yes, tactile gain, tactile bias, friction confounding, and noise.
- Uncertainty/error bars: no, because the decision is already negative under deterministic aggregate MSE.
- Real robot data: no.
- Decision: kill/archive.
