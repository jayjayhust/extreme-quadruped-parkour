# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Manager-based Go2 parkour environments registration.

Provides Flat, Rough, Play, and 5 ablation variants (+ their Play modes) = 14 task IDs.
"""

import gymnasium as gym

from . import agents

##
# Register Gym environments.
##

# -- Flat terrain --

gym.register(
    id="Go2-Parkour-Flat-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.rough_env_cfg:Go2ParkourFlatEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:Go2ParkourFlatPPORunnerCfg",
    },
)

# -- Rough terrain --

gym.register(
    id="Go2-Parkour-Rough-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.rough_env_cfg:Go2ParkourRoughEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:Go2ParkourRoughPPORunnerCfg",
    },
)

gym.register(
    id="Go2-Parkour-Rough-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.rough_env_cfg:Go2ParkourRoughPlayEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:Go2ParkourRoughPPORunnerCfg",
    },
)

# -- Ablation 1: no scan in policy --

gym.register(
    id="Go2-Parkour-Rough-Abl1-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.rough_env_cfg:Go2ParkourRoughAbl1EnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:Go2ParkourRoughAbl1PPORunnerCfg",
    },
)

gym.register(
    id="Go2-Parkour-Rough-Abl1-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.rough_env_cfg:Go2ParkourRoughAbl1PlayEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:Go2ParkourRoughAbl1PPORunnerCfg",
    },
)

# -- Ablation 2.5: scan-first ordering --

gym.register(
    id="Go2-Parkour-Rough-Abl2_5-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.rough_env_cfg:Go2ParkourRoughAbl2_5EnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:Go2ParkourRoughAbl2_5PPORunnerCfg",
    },
)

gym.register(
    id="Go2-Parkour-Rough-Abl2_5-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.rough_env_cfg:Go2ParkourRoughAbl2_5PlayEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:Go2ParkourRoughAbl2_5PPORunnerCfg",
    },
)

# -- Ablation 3.5: explicit scan encoder (same env cfg as Rough) --

gym.register(
    id="Go2-Parkour-Rough-Abl3_5-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.rough_env_cfg:Go2ParkourRoughEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:Go2ParkourRoughAbl3_5PPORunnerCfg",
    },
)

gym.register(
    id="Go2-Parkour-Rough-Abl3_5-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.rough_env_cfg:Go2ParkourRoughPlayEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:Go2ParkourRoughAbl3_5PPORunnerCfg",
    },
)

# -- Ablation 4.0: no scan encoding for critic (same env cfg as Rough) --

gym.register(
    id="Go2-Parkour-Rough-Abl4_0-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.rough_env_cfg:Go2ParkourRoughEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:Go2ParkourRoughAbl4_0PPORunnerCfg",
    },
)

gym.register(
    id="Go2-Parkour-Rough-Abl4_0-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.rough_env_cfg:Go2ParkourRoughPlayEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:Go2ParkourRoughAbl4_0PPORunnerCfg",
    },
)

# -- Ablation 7.0: reduced privileged encoder (same env cfg as Rough) --

gym.register(
    id="Go2-Parkour-Rough-Abl7_0-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.rough_env_cfg:Go2ParkourRoughEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:Go2ParkourRoughAbl7_0PPORunnerCfg",
    },
)

gym.register(
    id="Go2-Parkour-Rough-Abl7_0-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.rough_env_cfg:Go2ParkourRoughPlayEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:Go2ParkourRoughAbl7_0PPORunnerCfg",
    },
)
