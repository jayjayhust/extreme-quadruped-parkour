# Codex Changes

This README records updates made in the current workspace by the Codex assistant.

## Summary
- Raised the PhysX rigid contact patch buffer exclusively for the Go2 rough terrain config so training no longer overflows the GPU patch stream when many envs collide with irregular ground.

## Files Updated
- source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py:119
  - Inserted a `sim: SimulationCfg = Go2FlatEnvCfg().sim.replace(...)` override inside `Go2RoughEnvCfg` that lifts `physx.gpu_max_rigid_patch_count` to `12 * 2**15` (393,216) from the default 163,840.

## Usage Notes
- Launch training with `./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Go2-Rough-Direct-v0 --headless`; the increased buffer prevents the "Patch buffer overflow detected" PhysX errors observed during rough-terrain runs.

## Additional Context
- Logs showed PhysX requesting up to ~292k patches. The new buffer keeps headroom above that demand; monitor future runs and raise the multiplier further if Omniverse reports a higher minimum.
