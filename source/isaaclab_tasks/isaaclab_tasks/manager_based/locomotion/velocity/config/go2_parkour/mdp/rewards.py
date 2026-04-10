# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Custom reward functions for the Go2 parkour manager-based environment.

These replicate the reward terms from the direct Go2 environment that are not
available in the base isaaclab MDP module.
"""

from __future__ import annotations

import torch
from typing import TYPE_CHECKING

from isaaclab.assets import Articulation
from isaaclab.managers import SceneEntityCfg
from isaaclab.sensors import ContactSensor

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv

__all__ = [
    "torque_sum",
    "stop_penalty_lin",
    "stop_penalty_ang",
    "hip_pos_l2",
    "feet_stumble",
    "joint_deviation_l2",
    "mechanical_work",
]


def torque_sum(
    env: ManagerBasedRLEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Sum of applied joint torques (not squared). Shape: (num_envs,)."""
    asset: Articulation = env.scene[asset_cfg.name]
    return torch.sum(asset.data.applied_torque, dim=1)


def stop_penalty_lin(
    env: ManagerBasedRLEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Exponential penalty on linear velocity magnitude (penalizes being stopped).

    Returns exp(-2 * ||lin_vel_xy||^2). Shape: (num_envs,).
    """
    asset: Articulation = env.scene[asset_cfg.name]
    lin_vel_norm_sq = torch.sum(torch.square(asset.data.root_lin_vel_b[:, :2]), dim=1)
    return torch.exp(-2.0 * lin_vel_norm_sq)


def stop_penalty_ang(
    env: ManagerBasedRLEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Exponential penalty on angular velocity magnitude (penalizes being stopped).

    Returns exp(-2 * ||ang_vel_xy||^2). Shape: (num_envs,).
    """
    asset: Articulation = env.scene[asset_cfg.name]
    ang_vel_error = torch.sum(torch.square(asset.data.root_ang_vel_b[:, :2]), dim=1)
    return torch.exp(-2.0 * ang_vel_error)


def hip_pos_l2(
    env: ManagerBasedRLEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """L2 penalty on hip joint positions deviating from defaults.

    The asset_cfg should specify joint_names matching hip joints (e.g. ".*_hip_joint").
    Shape: (num_envs,).
    """
    asset: Articulation = env.scene[asset_cfg.name]
    hip_pos = asset.data.joint_pos[:, asset_cfg.joint_ids]
    hip_default = asset.data.default_joint_pos[:, asset_cfg.joint_ids]
    return torch.sum(torch.square(hip_pos - hip_default), dim=1)


def feet_stumble(
    env: ManagerBasedRLEnv,
    sensor_cfg: SceneEntityCfg,
    ratio: float = 4.0,
) -> torch.Tensor:
    """Stumble detection: penalize when horizontal contact force dominates vertical.

    Returns 1.0 if any foot has ||horizontal_force|| > ratio * |vertical_force|,
    0.0 otherwise. Shape: (num_envs,).
    """
    contact_sensor: ContactSensor = env.scene.sensors[sensor_cfg.name]
    net_contact_forces = contact_sensor.data.net_forces_w_history[:, -1, sensor_cfg.body_ids]  # (N, feet, 3)
    horiz_force = torch.norm(net_contact_forces[..., :2], dim=2)
    vert_force = torch.abs(net_contact_forces[..., 2])
    stumble = torch.any(horiz_force > (ratio * vert_force), dim=1).float()
    return stumble


def joint_deviation_l2(
    env: ManagerBasedRLEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """L2 penalty on all joint positions deviating from defaults.

    Unlike the base mdp's joint_deviation_l1, this uses the squared (L2) kernel.
    Shape: (num_envs,).
    """
    asset: Articulation = env.scene[asset_cfg.name]
    return torch.sum(
        torch.square(asset.data.joint_pos[:, asset_cfg.joint_ids] - asset.data.default_joint_pos[:, asset_cfg.joint_ids]),
        dim=1,
    )


def mechanical_work(
    env: ManagerBasedRLEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Positive mechanical work (regeneration clamped out).

    Computes sum(torque * joint_vel) and clamps to non-negative, then scales by step_dt.
    Shape: (num_envs,).
    """
    asset: Articulation = env.scene[asset_cfg.name]
    joint_power = torch.sum(asset.data.applied_torque * asset.data.joint_vel, dim=1)
    return torch.clamp_min(joint_power, 0.0) * env.step_dt
