# Codex Changes

This README records updates made in the current workspace by the Codex assistant.

## Summary
- Raised the PhysX rigid contact patch buffer exclusively for the Go2 rough terrain config so training no longer overflows the GPU patch stream when many envs collide with irregular ground.
- Added missing reward-scale parameters to keep the 3D-foot-space reward terms active without AttributeErrors.

## Files Updated
- source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py:119
  - Inserted a `sim: SimulationCfg = Go2FlatEnvCfg().sim.replace(...)` override inside `Go2RoughEnvCfg` that lifts `physx.gpu_max_rigid_patch_count` to `12 * 2**15` (393,216) from the default 163,840.
- source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py:101-114
  - Added `torque_reward_scale`, `stop_penalty_reward_scale`, and `dof_close_to_default_reward_scale` so the extended Go2 reward terms match the 3D-foot-space environment implementation.

## Usage Notes
- Launch training with `./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Go2-Rough-Direct-v0 --headless`; the increased buffer prevents the "Patch buffer overflow detected" PhysX errors observed during rough-terrain runs.

## Additional Context
- Logs showed PhysX requesting up to ~292k patches. The new buffer keeps headroom above that demand; monitor future runs and raise the multiplier further if Omniverse reports a higher minimum.
- The new reward-scale fields default to 0.0, preserving the original behaviour until you tune them for the 3D space reward shaping.
