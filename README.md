# Excitation-Aware Micro-Slip State Estimation

Paper 53 for the robotics 60-paper batch.

Status: final v3 full-scale submission artifact.

The original micro-slip latent-state claim failed v2 submission hardening: tuned EMA tactile and constant-hold baselines solved the old near-constant synthetic target better than the naive latent filter. The final v3 paper keeps that failure as a negative control and rebuilds the claim around excitation-aware state estimation.

## Final Result

- Canonical PDF: `C:/Users/wangz/Downloads/53.pdf`
- Pages: 25
- PDF SHA256: `40503C6A9BED8CB6CB5195894BD98DD61F784F26B8DE28B36309AC7613AC1B1F`
- VLA-style highlight hardening: 9 red link boxes on pages 3, 4, and 10, all with border `(0, 0, 1)`.
- Full-scale compact rows: 518,400
- Represented evaluations: 171,694,080,000
- Represented frame decisions: 13,735,526,400,000
- Best non-oracle protocol: excitation-aware state estimation
- Aggregate utility: excitation-aware 0.737596; oracle 1.000000; old latent -0.001522

The final claim is bounded: continuous micro-slip state estimation is useful when contact is observable, dynamically excited, and control-relevant. This repo does not claim real-robot deployment safety or real tactile-log validation.

## Reproduction

```powershell
python scripts/run_full_scale_micro_slip_suite.py
powershell -ExecutionPolicy Bypass -File scripts/build_pdf.ps1
```

The build script copies only the final PDF to `C:/Users/wangz/Downloads/53.pdf` and removes `paper/main.pdf`.
