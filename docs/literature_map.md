# Literature Map

## Sweep Summary
- Total sweep rows: 2058
- Serious skim set: 300
- Deep read set: 240
- Hostile prior set: 100

## Dominant Clusters
- manipulation: 1371
- tactile: 839
- contact: 696
- dynamics: 366
- slip: 167
- state: 63

## Emerging Thesis
- Existing work mostly treats slip as a binary detection label or a friction proxy.
- The literature under-serves micro-slip as a latent state that can be estimated continuously and used for control.
- The strongest niche is contact-local, tactile-first state estimation under dexterous grasp stabilization.

## 20 Hidden Assumptions To Attack
- slip onset is well-separated from gross slip
- binary labels capture control-relevant dynamics
- one sensor modality is enough
- contact patch geometry is static during inference
- friction is stationary over the grasp
- object compliance is negligible or can be absorbed into noise
- supervised labels are cheap and accurate
- training objects span deployment objects
- slip is observable from local kinematics alone
- slip can be treated independently from pose drift
- force thresholds generalize across grasps
- tactile sampling rate is always sufficient
- contact mode switching is rare enough to ignore
- grasp stabilization only needs detection, not state estimation
- the controller can react after slip is detected without loss
- latent stability is one-dimensional and monotonic
- gripper geometry does not matter much
- the environment does not adversarially perturb friction
- object motion and slip are equivalent signals
- annotation noise is small relative to the signal