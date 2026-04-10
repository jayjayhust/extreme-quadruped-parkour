# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""RSL-RL PPO runner configs for Go2 parkour manager-based environments.

These mirror the direct Go2 agent configs, using ActorCriticScan for scan encoding.
"""

from isaaclab.utils import configclass

from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg, RslRlPpoActorCriticCfg, RslRlPpoAlgorithmCfg


def _make_go2_parkour_rough_policy_cfg(
    *,
    num_actor_scan_obs: int | None = None,
    num_critic_scan_obs: int | None = None,
    scan_encoder_dims: list[int] | None = None,
    actor_scan_encoder_dims: list[int] | None = None,
    critic_scan_encoder_dims: list[int] | None = None,
    encode_scan_for_critic: bool = True,
    priv_obs_encoder_dims: list[int] | None = None,
    priv_encoder_dims: list[int] | None = None,
) -> RslRlPpoActorCriticCfg:
    if priv_encoder_dims is None:
        priv_encoder_dims = priv_obs_encoder_dims
    return RslRlPpoActorCriticCfg(
        class_name="ActorCriticScan",
        init_noise_std=1.0,
        noise_std_type="log",
        actor_hidden_dims=[512, 256, 128],
        critic_hidden_dims=[512, 256, 128],
        activation="elu",
        num_prop_obs=52,
        num_scan_obs=187,
        num_actor_scan_obs=num_actor_scan_obs,
        num_critic_scan_obs=num_critic_scan_obs,
        scan_encoder_dims=scan_encoder_dims,
        actor_scan_encoder_dims=actor_scan_encoder_dims,
        critic_scan_encoder_dims=critic_scan_encoder_dims,
        encode_scan_for_critic=encode_scan_for_critic,
        priv_obs_encoder_dims=priv_obs_encoder_dims,
        priv_encoder_dims=priv_encoder_dims,
    )


@configclass
class Go2ParkourFlatPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 24
    max_iterations = 5000
    save_interval = 50
    experiment_name = "go2_parkour_flat"
    empirical_normalization = True
    policy = RslRlPpoActorCriticCfg(
        class_name="ActorCriticScan",
        init_noise_std=0.5,
        actor_hidden_dims=[512, 256, 128],
        critic_hidden_dims=[512, 256, 128],
        activation="elu",
        noise_std_type="log",
        num_prop_obs=52,
        num_scan_obs=0,
        scan_encoder_dims=[128, 64, 32],
    )
    algorithm = RslRlPpoAlgorithmCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=0.01,
        num_learning_epochs=5,
        num_mini_batches=4,
        learning_rate=1.0e-4,
        schedule="adaptive",
        gamma=0.99,
        lam=0.95,
        desired_kl=0.01,
        max_grad_norm=1.0,
    )


@configclass
class Go2ParkourRoughPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 24
    max_iterations = 20000
    save_interval = 50
    experiment_name = "go2_parkour_rough"
    empirical_normalization = True
    policy = RslRlPpoActorCriticCfg(
        class_name="ActorCriticScan",
        init_noise_std=1.0,
        noise_std_type="log",
        actor_hidden_dims=[512, 256, 128],
        critic_hidden_dims=[512, 256, 128],
        activation="elu",
        num_prop_obs=52,
        num_scan_obs=187,
        scan_encoder_dims=[128, 64, 32],
    )
    algorithm = RslRlPpoAlgorithmCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=0.005,
        num_learning_epochs=5,
        num_mini_batches=4,
        learning_rate=1.0e-3,
        schedule="adaptive",
        gamma=0.99,
        lam=0.95,
        desired_kl=0.01,
        max_grad_norm=1.0,
    )


@configclass
class Go2ParkourRoughAbl1PPORunnerCfg(Go2ParkourRoughPPORunnerCfg):
    experiment_name = "go2_parkour_rough_abl1"
    policy = _make_go2_parkour_rough_policy_cfg(num_actor_scan_obs=0)


@configclass
class Go2ParkourRoughAbl2_5PPORunnerCfg(Go2ParkourRoughPPORunnerCfg):
    experiment_name = "go2_parkour_rough_abl2_5"
    policy = RslRlPpoActorCriticCfg(
        class_name="ActorCritic",
        init_noise_std=1.0,
        noise_std_type="log",
        actor_hidden_dims=[512, 256, 128],
        critic_hidden_dims=[512, 256, 128],
        activation="elu",
    )


@configclass
class Go2ParkourRoughAbl3_5PPORunnerCfg(Go2ParkourRoughPPORunnerCfg):
    experiment_name = "go2_parkour_rough_abl3_5"
    policy = _make_go2_parkour_rough_policy_cfg(scan_encoder_dims=[128, 64, 32])


@configclass
class Go2ParkourRoughAbl4_0PPORunnerCfg(Go2ParkourRoughPPORunnerCfg):
    experiment_name = "go2_parkour_rough_abl4_0"
    policy = _make_go2_parkour_rough_policy_cfg(
        scan_encoder_dims=[128, 64, 32],
        encode_scan_for_critic=False,
    )


@configclass
class Go2ParkourRoughAbl7_0PPORunnerCfg(Go2ParkourRoughPPORunnerCfg):
    experiment_name = "go2_parkour_rough_abl7_0"
    policy = _make_go2_parkour_rough_policy_cfg(
        scan_encoder_dims=[128, 64, 32],
        priv_encoder_dims=[64, 20],
    )
