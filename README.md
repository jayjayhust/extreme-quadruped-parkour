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

## Results Summary (Lab Meeting 04)
Common setup
- Terrain: 18 columns (7 types) x 10 levels; hardest tiles are Gap + Parkour Step
- Gap final width: 0.8 m; Parkour Step final height: 0.45 m (stairs max is 0.23 m)
- Train: 4096 envs, 20000 iterations; heading fixed (0 rad); collisions enabled
- Reward: Test25 scale; positive-work clamp to avoid rewarding negative work

Findings
- Abl 3.5 yields the **best mean reward and velocity tracking**; most stable in sim on Gap + Parkour Step
- Abl 1 fails due to blind walking (no scan access)
- Abl 2.5 struggles with high-dimensional raw scan (feature extraction issue)
- Abl 4.0 degrades due to critic receiving raw scan (noisy value estimation)
- Abl 7.0 degrades due to priv_obs encoding (constants overfitting)

Conclusion
- Use scan encoding for both actor and critic
- Avoid priv_obs encoding for critic

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
