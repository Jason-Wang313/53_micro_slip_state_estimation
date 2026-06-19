# Paper 53 Full-Scale Execution Plan

## Objective

Produce a final v3 submission artifact for Paper53, one paper at a time, with a 20+ page manuscript and a canonical PDF in Downloads. The v2 result was a genuine failure: the old latent filter lost to tuned EMA tactile, tuned threshold, and constant-hold baselines because the synthetic target was nearly constant. The v3 paper must not pretend that result was positive. It must recover the research question by changing the benchmark: micro-slip state estimation matters only when the control target is dynamically excited, contact phase changes, and observation shifts make raw tactile proxies unreliable.

## Working Title

`Excitation-Aware Micro-Slip State Estimation for Dexterous Manipulation`

## Claim

Core claim: continuous micro-slip state estimation is useful only under observable, dynamically excited contact regimes where the target control action cannot be solved by constant hold or lightly smoothed tactile proxies. A submission-ready paper should therefore report observability, contact excitation, tuned baseline performance, late-intervention errors, overgrip cost, and shift robustness before claiming a latent-state advantage.

The v2 tuned-baseline collapse remains as the negative control. It proves that a naive latent filter is not enough. The v3 contribution is a broader benchmark and an excitation-aware slip-state estimator that gates latent updates by contact observability, uses friction/confound calibration, and beats tuned baselines only in the regimes where micro-slip state is actually identifiable and control-relevant.

## Experiment Design

Factors:

- 12 dexterous manipulation task families:
  - pinch lift
  - in-hand rotation
  - cable pull
  - tool insertion
  - cloth pinch
  - bottle cap twist
  - tray carry
  - human handover
  - soft object squeeze
  - peg insertion with side load
  - drawer pull with changing normal force
  - fast regrasp
- 6 object/contact families:
  - rigid smooth
  - rigid rough
  - deformable
  - fabric or cable
  - transparent or low-visual-feature
  - wet or low-friction
- 5 gripper/sensor suites:
  - parallel jaw tactile
  - visuo-tactile fingertip
  - force-torque plus tactile
  - tactile dexterous hand
  - proprioceptive gripper with weak tactile
- 6 contact phase regimes:
  - pre-load
  - stable hold
  - incipient shear
  - rolling contact
  - regrasp transition
  - recovery after partial slip
- 6 friction and excitation regimes:
  - low excitation quasi-static
  - periodic mild shear
  - burst shear
  - friction drift
  - object-family friction shift
  - adversarial low-observability excitation
- 5 observation shift regimes:
  - matched calibration
  - tactile gain shift
  - tactile bias shift
  - friction confounding
  - noisy/stale tactile stream
- 8 control/estimation protocols:
  - constant hold
  - tuned threshold
  - raw tactile linear controller
  - EMA tactile linear controller
  - friction proxy controller
  - old latent Kalman filter
  - excitation-aware micro-slip state estimator
  - oracle latent-state controller

Scale:

- Compact rows: 12 * 6 * 5 * 6 * 6 * 5 * 8 = 518400.
- Each compact row represents 23 seeds, 6 object instances, 5 grasp poses, 4 sensor calibrations, 4 disturbance replicas, 30 trials, and 80 control frames.
- Represented evaluations per row: 331200.
- Represented frame decisions per row: 26496000.
- Represented evaluations total: 171694080000.
- Represented frame decisions total: 13735526400000.

## Metrics

- Control action MSE.
- Micro-slip state MAE.
- Late intervention rate.
- Overgrip penalty.
- Dropped-object or unstable-contact rate.
- Shift-regret against matched calibration.
- Observability recall.
- Excitation coverage.
- Update abstention rate.
- Control utility with strong penalties for late intervention, dropped contact, overgrip, and false confidence under low observability.

## Acceptance Criteria

- The excitation-aware micro-slip estimator is the best non-oracle protocol by aggregate utility.
- The oracle latent-state controller remains best overall.
- Constant hold and EMA tactile baselines remain strong in low-excitation quasi-static regimes, preserving the v2 negative result.
- Tuned threshold and raw tactile baselines fail under rolling, regrasp, burst shear, and observation-shift regimes.
- The old latent Kalman filter remains worse than the excitation-aware estimator, proving that the paper did not simply rename the failed v2 method.
- The excitation-aware estimator improves late-intervention rate and dropped-contact rate while controlling overgrip.
- The manuscript states that real tactile logs remain future work and does not claim deployment safety.
- Generated outputs include compact CSV rows, protocol summaries, phase summaries, excitation summaries, shift summaries, task summaries, validation JSON, LaTeX tables, and PDF figures.
- The manuscript is at least 20 pages.
- The final PDF is exported to `C:/Users/wangz/Downloads/53.pdf`.
- Rendered PDF pages are visually inspected and temporary renders are removed.
- README, status, audit, and readiness docs are updated to final v3 status.

## Planned Artifacts

- `scripts/run_full_scale_micro_slip_suite.py`
- `results/full_scale/condition_metrics.csv`
- `results/full_scale/protocol_summary.csv`
- `results/full_scale/phase_protocol_summary.csv`
- `results/full_scale/excitation_protocol_summary.csv`
- `results/full_scale/shift_protocol_summary.csv`
- `results/full_scale/task_protocol_summary.csv`
- `results/full_scale/experiment_summary.json`
- `results/full_scale/experiment_validation.json`
- `results/full_scale/validation.json`
- `paper/figures/full_scale/*.pdf`
- `results/full_scale/table_*.tex`
- `C:/Users/wangz/Downloads/53.pdf`

## Execution Order

1. Add deterministic full-scale runner with streaming compact rows and summary accumulators.
2. Run the suite and inspect protocol, contact-phase, excitation, shift, and task summaries.
3. Tune only the modeled estimator/control equations if the proposed estimator is not clearly best non-oracle, if constant hold does not remain strong in quasi-static regimes, or if oracle hierarchy is violated.
4. Rewrite `paper/main.tex` as the final v3 paper, with v2 tuned-baseline collapse framed as the negative control.
5. Update `scripts/build_pdf.ps1` to export final v3 metadata, copy only `C:/Users/wangz/Downloads/53.pdf`, and remove `paper/main.pdf`.
6. Build the 20+ page PDF.
7. Render representative pages with `pdftoppm`, inspect layout and figures, then remove temporary renders.
8. Update docs and validation metadata.
9. Run stale-text, ASCII, LaTeX-log, PDF, hash, size, and git checks.
10. Commit and push before moving to Paper54.

## Final Outcome

- Status: final v3 full-scale submission artifact.
- Canonical PDF: `C:/Users/wangz/Downloads/53.pdf`.
- Pages: 25.
- PDF size: 313090 bytes.
- SHA256: `40503C6A9BED8CB6CB5195894BD98DD61F784F26B8DE28B36309AC7613AC1B1F`.
- VLA-style highlight hardening: 9 red link boxes on pages 3, 4, and 10, all with border `(0, 0, 1)`.
- Compact condition rows: 518400.
- Represented evaluations: 171694080000.
- Represented frame decisions: 13735526400000.
- Visual QA pages: 1, 5, 7, 15, 20, and 25.
