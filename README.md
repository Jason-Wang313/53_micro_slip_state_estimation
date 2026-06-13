# Micro Slip State Estimation

Paper 53 for the robotics 60-paper batch.

Decision: kill/archive.

The original thesis was that micro-slip should be estimated as a continuous control-relevant latent state rather than treated only as a delayed binary event. Submission hardening found that the synthetic evidence does not support the claim. The proposed latent filter loses to simple tuned baselines:

- Matched generator: latent filter MSE 0.01453; EMA tactile baseline MSE 0.00021.
- Tactile bias shift: latent filter MSE 0.06434; constant hold MSE 0.00058.
- Friction confounding: latent filter MSE 0.05102; constant hold MSE 0.00058.

The result is a negative archive decision. A recoverable version needs real tactile/proprioceptive grasp logs, a nontrivial control target, and tuned continuous tactile baselines.

## Reproduction

```powershell
python scripts/run_micro_slip_diagnostic.py
python scripts/v2_tuned_baseline_stress.py
powershell -ExecutionPolicy Bypass -File scripts/build_pdf.ps1
```

The canonical built PDF is `C:/Users/wangz/Downloads/53.pdf`.

Local generated PDFs are not tracked. The build script copies the generated PDF to the canonical Downloads path and removes `paper/main.pdf`.
