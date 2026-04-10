# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Custom observation functions for the Go2 parkour manager-based environment.

These mirror the privileged and contact observations from the direct Go2 environment.
"""

from __future__ import annotations

import torch
from typing import TYPE_CHECKING

from isaaclab.assets import Articulation
from isaaclab.managers import SceneEntityCfg
from isaaclab.sensors import ContactSensor

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedEnv

__all__ = [
    "foot_contacts",
    "base_mass_obs",
    "base_com_obs",
    "friction_coeff_obs",
    "p_gain_scale_obs",
    "d_gain_scale_obs",
]


def foot_contacts(
    env: ManagerBasedEnv,
    sensor_cfg: SceneEntityCfg,
    threshold: float = 1.0,
) -> torch.Tensor:
    """Binary foot contact flags from contact sensor.

    Returns 1.0 for each foot body where the net contact force norm exceeds the threshold,
    0.0 otherwise. Shape: (num_envs, num_feet).
    """
    contact_sensor: ContactSensor = env.scene.sensors[sensor_cfg.name]
    net_contact_forces = contact_sensor.data.net_forces_w_history
    # use the latest time-step; body_ids selects only foot bodies
    foot_forces = net_contact_forces[:, -1, sensor_cfg.body_ids]  # (N, num_feet, 3)
    return (torch.norm(foot_forces, dim=-1) > threshold).float()


def base_mass_obs(
    env: ManagerBasedEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Base link mass after domain randomization. Shape: (num_envs, 1)."""
    asset: Articulation = env.scene[asset_cfg.name]
    masses = asset.root_physx_view.get_masses().to(env.device)  # (N, num_bodies)
    base_mass = masses[:, asset_cfg.body_ids]  # (N, 1) or (N, 1, 1)
    return base_mass.reshape(env.num_envs, -1)


def base_com_obs(
    env: ManagerBasedEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Base link center-of-mass position after domain randomization. Shape: (num_envs, 3)."""
    asset: Articulation = env.scene[asset_cfg.name]
    coms = asset.root_physx_view.get_coms().to(env.device)  # (N, num_bodies, 7) or (N, num_bodies, 3+4)
    base_com = coms[:, asset_cfg.body_ids, :3]  # (N, 1, 3)
    return base_com.reshape(env.num_envs, -1)


def friction_coeff_obs(
    env: ManagerBasedEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Mean static friction coefficient across all robot shapes. Shape: (num_envs, 1)."""
    asset: Articulation = env.scene[asset_cfg.name]
    materials = asset.root_physx_view.get_material_properties().to(env.device)  # (N, num_shapes, 3)
    static_friction = materials[:, :, 0]  # (N, num_shapes)
    return static_friction.mean(dim=1, keepdim=True)


def p_gain_scale_obs(
    env: ManagerBasedEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Ratio of current P-gains (stiffness) to default P-gains. Shape: (num_envs, num_joints)."""
    asset: Articulation = env.scene[asset_cfg.name]
    actuator = next(iter(asset.actuators.values()))
    cur_stiffness = actuator.stiffness
    default_stiffness = asset.data.default_joint_stiffness[:, actuator.joint_indices]
    scale = torch.ones_like(cur_stiffness)
    nonzero = torch.abs(default_stiffness) > 1e-6
    scale[nonzero] = cur_stiffness[nonzero] / default_stiffness[nonzero]
    return scale


def d_gain_scale_obs(
    env: ManagerBasedEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Ratio of current D-gains (damping) to default D-gains. Shape: (num_envs, num_joints)."""
    asset: Articulation = env.scene[asset_cfg.name]
    actuator = next(iter(asset.actuators.values()))
    cur_damping = actuator.damping
    default_damping = asset.data.default_joint_damping[:, actuator.joint_indices]
    scale = torch.ones_like(cur_damping)
    nonzero = torch.abs(default_damping) > 1e-6
    scale[nonzero] = cur_damping[nonzero] / default_damping[nonzero]
    return scale
