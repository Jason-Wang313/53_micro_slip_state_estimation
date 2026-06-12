# Novelty Boundary Map

- Not novel: generic slip detection, friction estimation, tactile grasp stabilization, and binary incipient-slip classification.
- Borderline: multimodal slip detection if the tactile channel is merely fused rather than made central.
- Stronger boundary: estimate micro-slip as a latent state that the controller can regulate directly.
- Strongest mechanism shift: treat micro-slip as a continuous contact-state variable with temporal persistence, not a threshold event.

## Rejected Directions
- Bigger model.
- More data.
- New benchmark only.
- Uncertainty as the main contribution.
- Active learning as the main contribution.
- LLM planner or RL controller.

## Proposed Direction
- Build a micro-slip state estimator that exposes a control-friendly latent variable and demonstrate that it improves stabilization over threshold slip detectors.