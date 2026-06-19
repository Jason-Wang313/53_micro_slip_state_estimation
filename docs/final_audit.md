# Final Audit

Paper-readiness judgment: final v3 full-scale submission artifact.

## Final Thesis

Micro-slip state estimation should be excitation-aware: it is useful when contact is observable, dynamically excited, and control-relevant, but it should not replace tuned tactile baselines as a blanket rule.

## Historical Negative Control

V2 hardening showed the original evidence was not submission-grade:

- Matched generator: latent filter MSE 0.01453; tuned EMA tactile MSE 0.00021.
- Tactile bias shift: latent filter MSE 0.06434; constant hold MSE 0.00058.
- Friction confound: latent filter MSE 0.05102; constant hold MSE 0.00058.

The final paper keeps this collapse and makes it the reason for the v3 excitation-aware benchmark.

## Full-Scale V3 Evidence

- Compact condition rows: 518,400.
- Represented evaluations: 171,694,080,000.
- Represented frame decisions: 13,735,526,400,000.
- Excitation-aware utility: 0.737596.
- Oracle utility: 1.000000.
- Old latent utility: -0.001522.
- Excitation-aware control MSE: 0.057579.
- Excitation-aware state MAE: 0.186109.
- Excitation-aware late intervention: 0.072274.
- Excitation-aware dropped contact: 0.002869.

## Artifact Policy

- Canonical PDF: `C:/Users/wangz/Downloads/53.pdf`.
- Canonical PDF pages: 25.
- Canonical PDF size: 313090 bytes.
- Canonical PDF SHA256: `40503C6A9BED8CB6CB5195894BD98DD61F784F26B8DE28B36309AC7613AC1B1F`.
- Local generated PDF policy: `paper/main.pdf` is ignored and removed after build.
- Desktop copy: absent.

## QA

- LaTeX warning scan: clean.
- Visual QA pages: 1, 5, 7, 15, 20, and 25.
- VLA-style highlight hardening: 9 red link boxes on pages 3, 4, and 10, all with border `(0, 0, 1)`.
- Highlight visual QA pages: 3, 4, and 10.
- Long method-name spacing was fixed with `xspace` before final hash recording.
