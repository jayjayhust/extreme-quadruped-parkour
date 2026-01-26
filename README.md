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
- Train: 4096 envs, 20000 iterations; heading fixed (0 rad); collisions enabled
- Reward: Test25 scale; positive-work clamp to avoid rewarding negative work

Terrain types (generator mix)
| Terrain | Description | Ranges / Params (m) |
| --- | --- | --- |
| boxes | scattered box bumps | bump height: 0.025-0.10 |
| random_rough | noisy rough surface | noise amp: 0.01-0.06 (step 0.01) |
| debris_field | sparse rocks/boxes/cylinders | count: 20-40; box L/W/T: 0.5-2.0 / 0.2-0.6 / 0.05-0.25; cyl R/L: 0.05-0.20 / 0.5-2.0 |
| gap_bar | run-up then gaps | gap width: 0.1-0.8; landing: 0.45; run-up: 8.0 |
| hurdle_strip | repeated hurdles | hurdle height: 0.05-0.30; gap: 0.7-2.0; thickness: 0.2; run-up: 3.0 |
| stairs_strip | up/down stairs | step height: 0.05-0.23; segment: 5.0; steps: 10; run-up: 3.0 |
| parkour_step | extreme stepping stones | step height: 0.1-0.45; step length: 0.3-1.5; steps: 6; run-up: 3.0 |

Findings
- Abl 3.5 yields the **best mean reward and velocity tracking**; most stable in sim on Gap + Parkour Step
- Abl 1 fails due to blind walking (no scan access)
- Abl 2.5 struggles with high-dimensional raw scan (feature extraction issue)
- Abl 4.0 degrades due to critic receiving raw scan (noisy value estimation)
- Abl 7.0 degrades due to priv_obs encoding (constants overfitting)

Conclusion
- Use scan encoding for both actor and critic
- Avoid priv_obs encoding for critic

## Train (for lighter training without rendering, add --headless)
- Abl 1: Actor = prop_obs only; Critic = prop_obs + priv_obs + raw scan
  ```bash
  ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Go2-Rough-Direct-Abl1-v0 \
    --num_envs 4096
  ```

- Abl 2.5: Actor = prop_obs + raw scan; Critic = prop_obs + priv_obs + raw scan
  ```bash
  ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Go2-Rough-Direct-Abl2_5-v0 \
    --num_envs 4096
  ```

- Abl 3.5(**Best**): Actor = prop_obs + scan encoding; Critic = prop_obs + priv_obs + scan encoding
  ```bash
  ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Go2-Rough-Direct-Abl3_5-v0 \
    --num_envs 4096
  ```

- Abl 4.0: Actor = prop_obs + scan encoding; Critic = prop_obs + priv_obs + raw scan
  ```bash
  ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Go2-Rough-Direct-Abl4_0-v0 \
    --num_envs 4096
  ```

- Abl 7.0: Actor = prop_obs + scan encoding; Critic = prop_obs + priv_obs encoding + scan encoding
  ```bash
  ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Go2-Rough-Direct-Abl7_0-v0 \
    --num_envs 4096
  ```

## Play / Validate (Change the Abl Number OR num_envs)
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Go2-Rough-Direct-Abl3_5-v0 \
  --num_envs 50 \
  --load_run <run_dir_name> \
  --checkpoint <checkpoint_file>
```

Logs land under `logs/rsl_rl/<experiment_name>/` (see runner config names in
`source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py`).
