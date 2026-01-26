# Go2 Extreme Parkour Network Ablation (Unified)

This branch consolidates the five Parkour Step network ablations into one codebase and exposes them as task IDs.

## Task IDs (Train / Play)
- Abl 1: `Go2-Rough-Direct-Abl1-v0` / `Go2-Rough-Direct-Abl1-Play-v0`
- Abl 2.5: `Go2-Rough-Direct-Abl2_5-v0` / `Go2-Rough-Direct-Abl2_5-Play-v0`
- Abl 3.5: `Go2-Rough-Direct-Abl3_5-v0` / `Go2-Rough-Direct-Abl3_5-Play-v0`
- Abl 4.0: `Go2-Rough-Direct-Abl4_0-v0` / `Go2-Rough-Direct-Abl4_0-Play-v0`
- Abl 7.0: `Go2-Rough-Direct-Abl7_0-v0` / `Go2-Rough-Direct-Abl7_0-Play-v0`

## Ablation Mapping
- Abl 1: Actor = prop_obs only; Critic = prop_obs + priv_obs + raw scan
- Abl 2.5: Actor = prop_obs + raw scan; Critic = prop_obs + priv_obs + raw scan
- Abl 3.5: Actor = prop_obs + scan encoding; Critic = prop_obs + priv_obs + scan encoding
- Abl 4.0: Actor = prop_obs + scan encoding; Critic = prop_obs + priv_obs + raw scan
- Abl 7.0: Actor = prop_obs + scan encoding; Critic = prop_obs + priv_obs encoding + scan encoding

## Train
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Go2-Rough-Direct-Abl3_5-v0 \
  --num_envs 4096
```

## Play / Validate
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Go2-Rough-Direct-Abl3_5-Play-v0 \
  --load_run <run_dir_name> \
  --checkpoint <checkpoint_file>
```

Logs land under `logs/rsl_rl/<experiment_name>/` (see runner config names in
`source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py`).
