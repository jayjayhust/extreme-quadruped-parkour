# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import math

import isaaclab.envs.mdp as mdp
import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg
from isaaclab.envs import DirectRLEnvCfg
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import ContactSensorCfg, RayCasterCfg, patterns
from isaaclab.sim import SimulationCfg
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.utils import configclass

##
# Pre-defined configs
##
from isaaclab_assets.robots.unitree import UNITREE_GO2_CFG  # isort: skip
from isaaclab.terrains.config.rough import ROUGH_TERRAINS_CFG  # isort: skip


@configclass
class EventCfg:
    """Configuration for randomization."""

    add_base_mass = EventTerm(
        func=mdp.randomize_rigid_body_mass,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="base"),
            "mass_distribution_params": (-1.0, 2.0),
            "operation": "add",
        },
    )

    base_com = EventTerm(
        func=mdp.randomize_rigid_body_com,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="base"),
            "com_range": {"x": (-0.1, 0.1), "y": (-0.1, 0.1), "z": (-0.1, 0.1)},
        },
    )

    randomize_pd = EventTerm(
        func=mdp.randomize_actuator_gains,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", joint_names=".*"),
            "stiffness_distribution_params": (0.9, 1.1),
            "damping_distribution_params": (0.9, 1.1),
            "distribution": "uniform",
            "operation": "scale",
        },
    )


@configclass
class Go2FlatEnvCfg(DirectRLEnvCfg):
    # env
    episode_length_s = 20.0
    decimation = 4
    action_scale = 0.25
    action_space = 12
    observation_space = 52
    state_space = 81  # 52 prop + 29 priv

    # simulation
    sim: SimulationCfg = SimulationCfg(
        dt=1 / 200,
        render_interval=decimation,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
    )
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane",
        collision_group=-1,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
        debug_vis=False,
    )

    # scene
    scene: InteractiveSceneCfg = InteractiveSceneCfg(num_envs=4096, env_spacing=4.0, replicate_physics=True)

    # events
    events: EventCfg = EventCfg()

    # robot
    robot: ArticulationCfg = UNITREE_GO2_CFG.replace(prim_path="/World/envs/env_.*/Robot")
    contact_sensor: ContactSensorCfg = ContactSensorCfg(
        prim_path="/World/envs/env_.*/Robot/.*", history_length=3, update_period=0.005, track_air_time=True
    )

    # reward scales
    lin_vel_reward_scale = 3.0
    yaw_rate_reward_scale = 1.5
    z_vel_reward_scale = -2.0
    ang_vel_reward_scale = -0.05
    joint_torque_reward_scale = -2.5e-5
    joint_accel_reward_scale = -2.5e-7
    action_rate_reward_scale = -0.01
    feet_air_time_reward_scale = 2.0
    undesired_contact_reward_scale = -0.0
    flat_orientation_reward_scale = -0.5
    base_height_reward_scale = -10.0
    torque_reward_scale = 0.0
    stop_penalty_reward_scale = 0.0
    dof_close_to_default_reward_scale = -0.05

    # Training/Playing 모드 전환을 유연하게 하려고 추가한 플래그 
    ## command / curriculum settings (overridden by rough configs as needed)
    command_mode: str = "random"  # "random" or "fixed"
    fixed_command: tuple[float, float, float] = (1.0, 0.0, 0.0)
    use_curriculum: bool = True
    heading_command: bool = False
    heading_resample_time_s: float = 10.0
    heading_control_stiffness: float = 0.5
    rel_heading_envs: float = 1.0
    rel_standing_envs: float = 0.02
    command_heading_range: tuple[float, float] = (-math.pi, math.pi)
    command_yaw_range: tuple[float, float] = (-1.0, 1.0)
    command_log_interval: int = 0
    command_log_env: int = 0


@configclass
class Go2RoughEnvCfg(Go2FlatEnvCfg):
    # env
    # policy: 52 prop + 187 scan = 239; critic: 52 prop + 29 priv + 187 scan = 268
    observation_space = 239
    state_space = 268

    sim: SimulationCfg = Go2FlatEnvCfg().sim.replace(
        physx=Go2FlatEnvCfg().sim.physx.replace(gpu_max_rigid_patch_count=12 * 2**15)
    )

    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="generator",
        terrain_generator=ROUGH_TERRAINS_CFG.replace(
            sub_terrains={
                **ROUGH_TERRAINS_CFG.sub_terrains,
                "boxes": ROUGH_TERRAINS_CFG.sub_terrains["boxes"].replace(grid_height_range=(0.025, 0.1)),
                "random_rough": ROUGH_TERRAINS_CFG.sub_terrains["random_rough"].replace(
                    noise_range=(0.01, 0.06),
                    noise_step=0.01,
                ),
            }
        ),
        max_init_terrain_level=5, # 사수님이 9였다가 1로 바꾸심 -> 내가 5로 바꿈
        collision_group=-1,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
        ),
        visual_material=sim_utils.MdlFileCfg(
            mdl_path="{NVIDIA_NUCLEUS_DIR}/Materials/Base/Architecture/Shingles_01.mdl",
            project_uvw=True,
        ),
        debug_vis=False,
    )

    # we add a height scanner for perceptive locomotion
    height_scanner = RayCasterCfg(
        prim_path="/World/envs/env_.*/Robot/base",
        offset=RayCasterCfg.OffsetCfg(pos=(0.0, 0.0, 20.0)),
        ray_alignment="yaw",
        pattern_cfg=patterns.GridPatternCfg(resolution=0.1, size=[1.6, 1.0]),
        debug_vis=False,
        mesh_prim_paths=["/World/ground"],
    )

    # Test5 reward scales (override from flat config)
    base_height_reward_scale = 0.0 # Test4 (considering managerbased curriculum)
    flat_orientation_reward_scale = 0.0 # 험지니까 몸이 엄청 기울거라서
    feet_air_time_reward_scale = 0.125 # Test4 (considering managerbased curriculum)
    lin_vel_reward_scale = 2.5 # Test5에서는 더 크게 (considering managerbased curriculum)
    yaw_rate_reward_scale = 2.0 # Test5에서는 더 작게 (considering managerbased curriculum)
    z_vel_reward_scale = -2.0
    ang_vel_reward_scale = -0.05
    joint_torque_reward_scale = -2.5e-5
    joint_accel_reward_scale = -2.5e-7
    action_rate_reward_scale = -0.01
    undesired_contact_reward_scale = -0.8 # Test4 (considering managerbased curriculum)
    torque_reward_scale = 0.0
    stop_penalty_reward_scale = 0.0
    dof_close_to_default_reward_scale = 0.0 # Test4 (considering managerbased curriculum)

    # keep curriculum active and random commands for training
    command_mode: str = "random"
    use_curriculum: bool = True
    heading_command: bool = True


@configclass
class Go2RoughPlayEnvCfg(Go2RoughEnvCfg):
    """Evaluation configuration for Go2 rough terrain."""

    # disable curriculum updates so difficulty stays fixed per reset
    use_curriculum: bool = False

    # run with fixed velocity commands during playbacks
    command_mode: str = "fixed"
    fixed_command: tuple[float, float, float] = (1.0, 0.0, 0.0)

    # generate a different random rough terrain by changing the seed and disabling curriculum in generator
    terrain = Go2RoughEnvCfg().terrain.replace(
        terrain_generator=ROUGH_TERRAINS_CFG.replace(curriculum=False, seed=424242)
    )
