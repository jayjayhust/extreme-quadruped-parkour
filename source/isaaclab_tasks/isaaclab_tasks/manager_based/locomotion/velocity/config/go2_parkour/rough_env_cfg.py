# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Manager-based environment configs for Go2 parkour locomotion.

This mirrors the direct Go2 environment (direct/go2/) but uses the manager-based
ManagerBasedRLEnvCfg pattern. It includes rough/flat/play variants and all ablation
study configs.
"""

import math

import isaaclab.envs.mdp as mdp
import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.managers import CurriculumTermCfg as CurrTerm
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import ContactSensorCfg, RayCasterCfg, patterns
from isaaclab.sim import SimulationCfg
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.terrains.trimesh.mesh_terrains_cfg import (
    MeshDebrisTerrainCfg,
    MeshGapStripTerrainCfg,
    MeshHurdleStripTerrainCfg,
    MeshParkourStepTerrainCfg,
    MeshStairsStripTerrainCfg,
)
from isaaclab.utils import configclass
from isaaclab.utils.assets import ISAAC_NUCLEUS_DIR

import isaaclab_tasks.manager_based.locomotion.velocity.mdp as vel_mdp

from .mdp import observations as parkour_obs
from .mdp import rewards as parkour_rew

##
# Pre-defined configs
##
from isaaclab_assets.robots.unitree import UNITREE_GO2_CFG  # isort: skip
from isaaclab.terrains.config.rough import ROUGH_TERRAINS_CFG  # isort: skip


##
# Scene definition
##


@configclass
class Go2ParkourSceneCfg(InteractiveSceneCfg):
    """Scene configuration for Go2 parkour with custom terrains."""

    # ground terrain - 7 custom sub-terrain types for parkour
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="generator",
        terrain_generator=ROUGH_TERRAINS_CFG.replace(
            size=(23.0, 6.0),
            num_rows=10,
            num_cols=18,
            sub_terrains={
                "boxes": ROUGH_TERRAINS_CFG.sub_terrains["boxes"].replace(
                    proportion=(2 / 18), grid_height_range=(0.025, 0.1)
                ),
                "random_rough": ROUGH_TERRAINS_CFG.sub_terrains["random_rough"].replace(
                    proportion=(2 / 18), noise_range=(0.01, 0.06), noise_step=0.01
                ),
                "debris_field": MeshDebrisTerrainCfg(
                    proportion=(2 / 18),
                    size=(23.0, 23.0),
                    num_debris_min=20,
                    num_debris_max=40,
                    ground_thickness=0.1,
                    box_length_range=(0.5, 2.0),
                    box_width_range=(0.2, 0.6),
                    box_thickness_range=(0.05, 0.25),
                    cyl_radius_range=(0.05, 0.2),
                    cyl_length_range=(0.5, 2.0),
                ),
                "gap_bar": MeshGapStripTerrainCfg(
                    proportion=(3 / 18),
                    size=(23.0, 23.0),
                    gap_width_range=(0.1, 0.8),
                    landing_length=0.45,
                    start_platform_length=8.0,
                ),
                "hurdle_strip": MeshHurdleStripTerrainCfg(
                    proportion=(3 / 18),
                    size=(23.0, 23.0),
                    hurdle_height_range=(0.05, 0.3),
                    hurdle_thickness=0.2,
                    hurdle_gap_range=(0.7, 2.0),
                    start_platform_length=3.0,
                ),
                "stairs_strip": MeshStairsStripTerrainCfg(
                    proportion=(3 / 18),
                    size=(23.0, 23.0),
                    start_platform_length=3.0,
                    segment_length=5.0,
                    step_height_range=(0.05, 0.23),
                    steps_per_segment=10,
                    pattern=("up", "down", "up", "down"),
                ),
                "parkour_step": MeshParkourStepTerrainCfg(
                    proportion=(3 / 18),
                    size=(23.0, 23.0),
                    start_platform_length=3.0,
                    step_height_range=(0.1, 0.45),
                    step_length_base_range=(0.3, 1.5),
                    steps=6,
                ),
            },
        ),
        max_init_terrain_level=5,
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

    # robot - Unitree Go2 with self-collisions
    robot: ArticulationCfg = UNITREE_GO2_CFG.replace(
        prim_path="{ENV_REGEX_NS}/Robot",
        spawn=UNITREE_GO2_CFG.spawn.replace(
            articulation_props=UNITREE_GO2_CFG.spawn.articulation_props.replace(
                enabled_self_collisions=True,
                solver_position_iteration_count=8,
                solver_velocity_iteration_count=2,
            )
        ),
    )

    # sensors
    height_scanner = RayCasterCfg(
        prim_path="{ENV_REGEX_NS}/Robot/base",
        offset=RayCasterCfg.OffsetCfg(pos=(0.0, 0.0, 20.0)),
        ray_alignment="yaw",
        pattern_cfg=patterns.GridPatternCfg(resolution=0.1, size=[1.6, 1.0]),
        debug_vis=False,
        mesh_prim_paths=["/World/ground"],
    )
    contact_forces = ContactSensorCfg(
        prim_path="{ENV_REGEX_NS}/Robot/.*",
        history_length=3,
        update_period=0.005,
        track_air_time=True,
    )

    # lights
    sky_light = AssetBaseCfg(
        prim_path="/World/skyLight",
        spawn=sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75)),
    )


##
# MDP settings
##


@configclass
class Go2ParkourCommandsCfg:
    """Command specifications for Go2 parkour (rough terrain: heading mode, fixed 1 m/s)."""

    base_velocity = vel_mdp.UniformVelocityCommandCfg(
        asset_name="robot",
        resampling_time_range=(10.0, 10.0),
        rel_standing_envs=0.0,
        rel_heading_envs=1.0,
        heading_command=True,
        heading_control_stiffness=0.8,
        debug_vis=False,
        ranges=vel_mdp.UniformVelocityCommandCfg.Ranges(
            lin_vel_x=(1.0, 1.0),
            lin_vel_y=(0.0, 0.0),
            ang_vel_z=(-1.0, 1.0),
            heading=(0.0, 0.0),
        ),
    )


@configclass
class Go2ParkourActionsCfg:
    """Action specifications for Go2 parkour."""

    joint_pos = mdp.JointPositionActionCfg(
        asset_name="robot", joint_names=[".*"], scale=0.25, use_default_offset=True
    )


@configclass
class Go2ParkourObservationsCfg:
    """Observation specifications for Go2 parkour (asymmetric actor-critic)."""

    @configclass
    class PolicyCfg(ObsGroup):
        """Actor observations: 52D proprioceptive + optional 187D height scan."""

        # -- proprioceptive (52D total, order matches direct env exactly) --
        joint_pos_rel = ObsTerm(func=mdp.joint_pos_rel)  # 12D
        joint_vel = ObsTerm(func=mdp.joint_vel)  # 12D
        projected_gravity = ObsTerm(func=mdp.projected_gravity)  # 3D
        base_lin_vel = ObsTerm(func=mdp.base_lin_vel)  # 3D
        base_ang_vel = ObsTerm(func=mdp.base_ang_vel)  # 3D
        velocity_commands = ObsTerm(func=mdp.generated_commands, params={"command_name": "base_velocity"})  # 3D
        actions = ObsTerm(func=mdp.last_action)  # 12D
        foot_contacts = ObsTerm(
            func=parkour_obs.foot_contacts,
            params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot"), "threshold": 1.0},
        )  # 4D
        # -- height scan (187D) --
        height_scan = ObsTerm(
            func=mdp.height_scan,
            params={"sensor_cfg": SceneEntityCfg("height_scanner")},
            clip=(-1.0, 1.0),
        )

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = True

    @configclass
    class CriticCfg(ObsGroup):
        """Critic observations: 52D prop + 29D privileged + optional 187D height scan."""

        # -- proprioceptive (52D, same order as policy) --
        joint_pos_rel = ObsTerm(func=mdp.joint_pos_rel)
        joint_vel = ObsTerm(func=mdp.joint_vel)
        projected_gravity = ObsTerm(func=mdp.projected_gravity)
        base_lin_vel = ObsTerm(func=mdp.base_lin_vel)
        base_ang_vel = ObsTerm(func=mdp.base_ang_vel)
        velocity_commands = ObsTerm(func=mdp.generated_commands, params={"command_name": "base_velocity"})
        actions = ObsTerm(func=mdp.last_action)
        foot_contacts = ObsTerm(
            func=parkour_obs.foot_contacts,
            params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot"), "threshold": 1.0},
        )
        # -- privileged observations (29D) --
        base_mass = ObsTerm(
            func=parkour_obs.base_mass_obs,
            params={"asset_cfg": SceneEntityCfg("robot", body_names="base")},
        )  # 1D
        base_com = ObsTerm(
            func=parkour_obs.base_com_obs,
            params={"asset_cfg": SceneEntityCfg("robot", body_names="base")},
        )  # 3D
        friction_coeff = ObsTerm(
            func=parkour_obs.friction_coeff_obs,
            params={"asset_cfg": SceneEntityCfg("robot")},
        )  # 1D
        p_gain_scale = ObsTerm(
            func=parkour_obs.p_gain_scale_obs,
            params={"asset_cfg": SceneEntityCfg("robot")},
        )  # 12D
        d_gain_scale = ObsTerm(
            func=parkour_obs.d_gain_scale_obs,
            params={"asset_cfg": SceneEntityCfg("robot")},
        )  # 12D
        # -- height scan (187D) --
        height_scan = ObsTerm(
            func=mdp.height_scan,
            params={"sensor_cfg": SceneEntityCfg("height_scanner")},
            clip=(-1.0, 1.0),
        )

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = True

    # observation groups
    policy: PolicyCfg = PolicyCfg()
    critic: CriticCfg = CriticCfg()


@configclass
class Go2ParkourEventCfg:
    """Domain randomization events for Go2 parkour."""

    # -- startup events --
    physics_material = EventTerm(
        func=mdp.randomize_rigid_body_material,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=".*"),
            "static_friction_range": (0.7, 1.4),
            "dynamic_friction_range": (0.7, 1.4),
            "restitution_range": (0.0, 0.0),
            "num_buckets": 64,
        },
    )

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

    # -- reset events --
    reset_base = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {"x": (0.0, 0.0), "y": (0.0, 0.0), "yaw": (0.0, 0.0)},
            "velocity_range": {
                "x": (0.0, 0.0),
                "y": (0.0, 0.0),
                "z": (0.0, 0.0),
                "roll": (0.0, 0.0),
                "pitch": (0.0, 0.0),
                "yaw": (0.0, 0.0),
            },
        },
    )

    reset_robot_joints = EventTerm(
        func=mdp.reset_joints_by_scale,
        mode="reset",
        params={
            "position_range": (1.0, 1.0),
            "velocity_range": (0.0, 0.0),
        },
    )


@configclass
class Go2ParkourRewardsCfg:
    """Reward terms for Go2 parkour (flat terrain defaults)."""

    # -- task tracking --
    track_lin_vel_xy_exp = RewTerm(
        func=mdp.track_lin_vel_xy_exp,
        weight=3.0,
        params={"command_name": "base_velocity", "std": math.sqrt(0.25)},
    )
    track_ang_vel_z_exp = RewTerm(
        func=mdp.track_ang_vel_z_exp,
        weight=1.5,
        params={"command_name": "base_velocity", "std": math.sqrt(0.25)},
    )
    # -- penalties --
    lin_vel_z_l2 = RewTerm(func=mdp.lin_vel_z_l2, weight=-2.0)
    ang_vel_xy_l2 = RewTerm(func=mdp.ang_vel_xy_l2, weight=-0.05)
    dof_torques_l2 = RewTerm(func=mdp.joint_torques_l2, weight=-2.5e-5)
    dof_acc_l2 = RewTerm(func=mdp.joint_acc_l2, weight=-2.5e-7)
    action_rate_l2 = RewTerm(func=mdp.action_rate_l2, weight=-0.01)
    feet_air_time = RewTerm(
        func=vel_mdp.feet_air_time,
        weight=2.0,
        params={
            "sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot"),
            "command_name": "base_velocity",
            "threshold": 0.5,
        },
    )
    undesired_contacts = RewTerm(
        func=mdp.undesired_contacts,
        weight=-0.0,
        params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_thigh"), "threshold": 1.0},
    )
    flat_orientation_l2 = RewTerm(func=mdp.flat_orientation_l2, weight=-0.5)
    base_height = RewTerm(
        func=mdp.base_height_l2,
        weight=-10.0,
        params={"target_height": 0.3, "sensor_cfg": SceneEntityCfg("height_scanner")},
    )
    # -- custom parkour rewards --
    torque_sum = RewTerm(func=parkour_rew.torque_sum, weight=0.0)
    stop_penalty_lin = RewTerm(func=parkour_rew.stop_penalty_lin, weight=0.0)
    stop_penalty_ang = RewTerm(func=parkour_rew.stop_penalty_ang, weight=0.0)
    hip_pos = RewTerm(
        func=parkour_rew.hip_pos_l2,
        weight=-0.5,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=".*_hip_joint")},
    )
    feet_stumble = RewTerm(
        func=parkour_rew.feet_stumble,
        weight=-1.0,
        params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot"), "ratio": 4.0},
    )
    dof_close_to_default = RewTerm(func=parkour_rew.joint_deviation_l2, weight=-0.05)
    work = RewTerm(func=parkour_rew.mechanical_work, weight=-0.01)


@configclass
class Go2ParkourTerminationsCfg:
    """Termination terms for Go2 parkour."""

    time_out = DoneTerm(func=mdp.time_out, time_out=True)
    base_contact = DoneTerm(
        func=mdp.illegal_contact,
        params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names="base"), "threshold": 1.0},
    )


@configclass
class Go2ParkourCurriculumCfg:
    """Curriculum terms for Go2 parkour."""

    terrain_levels = CurrTerm(func=vel_mdp.terrain_levels_vel)


##
# Environment configuration
##


@configclass
class Go2ParkourRoughEnvCfg(ManagerBasedRLEnvCfg):
    """Manager-based config for Go2 parkour rough terrain training."""

    # Scene settings
    scene: Go2ParkourSceneCfg = Go2ParkourSceneCfg(num_envs=4096, env_spacing=4.0)
    # Basic settings
    observations: Go2ParkourObservationsCfg = Go2ParkourObservationsCfg()
    actions: Go2ParkourActionsCfg = Go2ParkourActionsCfg()
    commands: Go2ParkourCommandsCfg = Go2ParkourCommandsCfg()
    # MDP settings
    rewards: Go2ParkourRewardsCfg = Go2ParkourRewardsCfg()
    terminations: Go2ParkourTerminationsCfg = Go2ParkourTerminationsCfg()
    events: Go2ParkourEventCfg = Go2ParkourEventCfg()
    curriculum: Go2ParkourCurriculumCfg = Go2ParkourCurriculumCfg()

    def __post_init__(self):
        """Post initialization."""
        # general settings
        self.decimation = 4
        self.episode_length_s = 20.0
        # simulation settings
        self.sim.dt = 0.005
        self.sim.render_interval = self.decimation
        self.sim.physics_material = self.scene.terrain.physics_material
        self.sim.physx.gpu_max_rigid_patch_count = 12 * 2**15
        # update sensor update periods
        if self.scene.height_scanner is not None:
            self.scene.height_scanner.update_period = self.decimation * self.sim.dt
            # https://isaac-sim.github.io/IsaacLab/main/source/api/lab/isaaclab.sensors.html#isaaclab.sensors.RayCasterCfg.debug_vis
            self.scene.height_scanner.debug_vis = True  # debug visualization
        if self.scene.contact_forces is not None:
            self.scene.contact_forces.update_period = self.sim.dt
            # https://isaac-sim.github.io/IsaacLab/main/source/api/lab/isaaclab.sensors.html#isaaclab.sensors.ContactSensorCfg.debug_vis
            self.scene.contact_forces.debug_vis = True  # debug visualization

        # enable curriculum for terrain generator
        if getattr(self.curriculum, "terrain_levels", None) is not None:
            if self.scene.terrain.terrain_generator is not None:
                self.scene.terrain.terrain_generator.curriculum = True
        else:
            if self.scene.terrain.terrain_generator is not None:
                self.scene.terrain.terrain_generator.curriculum = False

        # -- rough terrain reward overrides (from Go2RoughEnvCfg) --
        self.rewards.base_height.weight = 0.0
        self.rewards.flat_orientation_l2.weight = 0.0
        self.rewards.feet_air_time.weight = 0.125
        self.rewards.lin_vel_z_l2.weight = -0.0
        self.rewards.undesired_contacts.weight = -0.8
        self.rewards.dof_close_to_default.weight = -0.01
        self.rewards.work.weight = -0.003
        self.rewards.hip_pos.weight = -0.3
        self.rewards.feet_stumble.weight = -0.0


##
# Variant configs
##


@configclass
class Go2ParkourFlatEnvCfg(Go2ParkourRoughEnvCfg):
    """Go2 parkour on flat terrain."""

    def __post_init__(self):
        super().__post_init__()

        # change terrain to flat
        self.scene.terrain.terrain_type = "plane"
        self.scene.terrain.terrain_generator = None
        # no height scan
        self.scene.height_scanner = None
        self.observations.policy.height_scan = None
        self.observations.critic.height_scan = None
        # no terrain curriculum
        self.curriculum.terrain_levels = None

        # flat commands: random mode
        self.commands.base_velocity = vel_mdp.UniformVelocityCommandCfg(
            asset_name="robot",
            resampling_time_range=(10.0, 10.0),
            rel_standing_envs=0.02,
            rel_heading_envs=1.0,
            heading_command=False,
            heading_control_stiffness=0.5,
            debug_vis=False,
            ranges=vel_mdp.UniformVelocityCommandCfg.Ranges(
                lin_vel_x=(-1.0, 1.0),
                lin_vel_y=(-1.0, 1.0),
                ang_vel_z=(-1.0, 1.0),
                heading=(-math.pi, math.pi),
            ),
        )

        # flat terrain reward overrides (restore flat defaults)
        self.rewards.track_lin_vel_xy_exp.weight = 3.0
        self.rewards.track_ang_vel_z_exp.weight = 1.5
        self.rewards.lin_vel_z_l2.weight = -2.0
        self.rewards.flat_orientation_l2.weight = -0.5
        self.rewards.base_height.weight = -10.0
        self.rewards.feet_air_time.weight = 2.0
        self.rewards.undesired_contacts.weight = -0.0
        self.rewards.dof_close_to_default.weight = -0.05
        self.rewards.work.weight = -0.01
        self.rewards.hip_pos.weight = -0.5
        self.rewards.feet_stumble.weight = -1.0


@configclass
class Go2ParkourRoughPlayEnvCfg(Go2ParkourRoughEnvCfg):
    """Go2 parkour rough terrain evaluation / play mode."""

    def __post_init__(self):
        super().__post_init__()

        # smaller scene for visualization
        self.scene.num_envs = 50
        self.scene.env_spacing = 4.0

        # disable curriculum, use different seed
        self.curriculum.terrain_levels = None
        if self.scene.terrain.terrain_generator is not None:
            self.scene.terrain.terrain_generator.curriculum = False
            self.scene.terrain.terrain_generator.seed = 424242
        self.scene.terrain.max_init_terrain_level = None


# -- Ablation 1: no scan in policy --


@configclass
class Go2ParkourRoughAbl1EnvCfg(Go2ParkourRoughEnvCfg):
    """Ablation 1: remove height scan from policy (actor sees only 52D prop)."""

    def __post_init__(self):
        super().__post_init__()
        self.observations.policy.height_scan = None


@configclass
class Go2ParkourRoughAbl1PlayEnvCfg(Go2ParkourRoughPlayEnvCfg):
    """Ablation 1 play mode."""

    def __post_init__(self):
        super().__post_init__()
        self.observations.policy.height_scan = None


# -- Ablation 2.5: scan-first ordering --


@configclass
class Go2ParkourRoughAbl2_5EnvCfg(Go2ParkourRoughEnvCfg):
    """Ablation 2.5: scan comes first in observation concatenation.

    Redefine observation groups with height_scan declared before proprioceptive terms.
    """

    def __post_init__(self):
        super().__post_init__()

        @configclass
        class ScanFirstPolicyCfg(ObsGroup):
            """Policy observations with scan before prop."""

            height_scan = ObsTerm(
                func=mdp.height_scan,
                params={"sensor_cfg": SceneEntityCfg("height_scanner")},
                clip=(-1.0, 1.0),
            )
            joint_pos_rel = ObsTerm(func=mdp.joint_pos_rel)
            joint_vel = ObsTerm(func=mdp.joint_vel)
            projected_gravity = ObsTerm(func=mdp.projected_gravity)
            base_lin_vel = ObsTerm(func=mdp.base_lin_vel)
            base_ang_vel = ObsTerm(func=mdp.base_ang_vel)
            velocity_commands = ObsTerm(func=mdp.generated_commands, params={"command_name": "base_velocity"})
            actions = ObsTerm(func=mdp.last_action)
            foot_contacts = ObsTerm(
                func=parkour_obs.foot_contacts,
                params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot"), "threshold": 1.0},
            )

            def __post_init__(self):
                self.enable_corruption = False
                self.concatenate_terms = True

        @configclass
        class ScanFirstCriticCfg(ObsGroup):
            """Critic observations with scan before prop + priv."""

            height_scan = ObsTerm(
                func=mdp.height_scan,
                params={"sensor_cfg": SceneEntityCfg("height_scanner")},
                clip=(-1.0, 1.0),
            )
            # privileged first (matching direct env scan_first_critic order: [scan, priv, prop])
            base_mass = ObsTerm(
                func=parkour_obs.base_mass_obs,
                params={"asset_cfg": SceneEntityCfg("robot", body_names="base")},
            )
            base_com = ObsTerm(
                func=parkour_obs.base_com_obs,
                params={"asset_cfg": SceneEntityCfg("robot", body_names="base")},
            )
            friction_coeff = ObsTerm(
                func=parkour_obs.friction_coeff_obs,
                params={"asset_cfg": SceneEntityCfg("robot")},
            )
            p_gain_scale = ObsTerm(
                func=parkour_obs.p_gain_scale_obs,
                params={"asset_cfg": SceneEntityCfg("robot")},
            )
            d_gain_scale = ObsTerm(
                func=parkour_obs.d_gain_scale_obs,
                params={"asset_cfg": SceneEntityCfg("robot")},
            )
            # proprioceptive
            joint_pos_rel = ObsTerm(func=mdp.joint_pos_rel)
            joint_vel = ObsTerm(func=mdp.joint_vel)
            projected_gravity = ObsTerm(func=mdp.projected_gravity)
            base_lin_vel = ObsTerm(func=mdp.base_lin_vel)
            base_ang_vel = ObsTerm(func=mdp.base_ang_vel)
            velocity_commands = ObsTerm(func=mdp.generated_commands, params={"command_name": "base_velocity"})
            actions = ObsTerm(func=mdp.last_action)
            foot_contacts = ObsTerm(
                func=parkour_obs.foot_contacts,
                params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot"), "threshold": 1.0},
            )

            def __post_init__(self):
                self.enable_corruption = False
                self.concatenate_terms = True

        self.observations.policy = ScanFirstPolicyCfg()
        self.observations.critic = ScanFirstCriticCfg()


@configclass
class Go2ParkourRoughAbl2_5PlayEnvCfg(Go2ParkourRoughPlayEnvCfg):
    """Ablation 2.5 play mode."""

    def __post_init__(self):
        super().__post_init__()

        @configclass
        class ScanFirstPolicyCfg(ObsGroup):
            height_scan = ObsTerm(
                func=mdp.height_scan,
                params={"sensor_cfg": SceneEntityCfg("height_scanner")},
                clip=(-1.0, 1.0),
            )
            joint_pos_rel = ObsTerm(func=mdp.joint_pos_rel)
            joint_vel = ObsTerm(func=mdp.joint_vel)
            projected_gravity = ObsTerm(func=mdp.projected_gravity)
            base_lin_vel = ObsTerm(func=mdp.base_lin_vel)
            base_ang_vel = ObsTerm(func=mdp.base_ang_vel)
            velocity_commands = ObsTerm(func=mdp.generated_commands, params={"command_name": "base_velocity"})
            actions = ObsTerm(func=mdp.last_action)
            foot_contacts = ObsTerm(
                func=parkour_obs.foot_contacts,
                params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot"), "threshold": 1.0},
            )

            def __post_init__(self):
                self.enable_corruption = False
                self.concatenate_terms = True

        @configclass
        class ScanFirstCriticCfg(ObsGroup):
            height_scan = ObsTerm(
                func=mdp.height_scan,
                params={"sensor_cfg": SceneEntityCfg("height_scanner")},
                clip=(-1.0, 1.0),
            )
            base_mass = ObsTerm(
                func=parkour_obs.base_mass_obs,
                params={"asset_cfg": SceneEntityCfg("robot", body_names="base")},
            )
            base_com = ObsTerm(
                func=parkour_obs.base_com_obs,
                params={"asset_cfg": SceneEntityCfg("robot", body_names="base")},
            )
            friction_coeff = ObsTerm(
                func=parkour_obs.friction_coeff_obs,
                params={"asset_cfg": SceneEntityCfg("robot")},
            )
            p_gain_scale = ObsTerm(
                func=parkour_obs.p_gain_scale_obs,
                params={"asset_cfg": SceneEntityCfg("robot")},
            )
            d_gain_scale = ObsTerm(
                func=parkour_obs.d_gain_scale_obs,
                params={"asset_cfg": SceneEntityCfg("robot")},
            )
            joint_pos_rel = ObsTerm(func=mdp.joint_pos_rel)
            joint_vel = ObsTerm(func=mdp.joint_vel)
            projected_gravity = ObsTerm(func=mdp.projected_gravity)
            base_lin_vel = ObsTerm(func=mdp.base_lin_vel)
            base_ang_vel = ObsTerm(func=mdp.base_ang_vel)
            velocity_commands = ObsTerm(func=mdp.generated_commands, params={"command_name": "base_velocity"})
            actions = ObsTerm(func=mdp.last_action)
            foot_contacts = ObsTerm(
                func=parkour_obs.foot_contacts,
                params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot"), "threshold": 1.0},
            )

            def __post_init__(self):
                self.enable_corruption = False
                self.concatenate_terms = True

        self.observations.policy = ScanFirstPolicyCfg()
        self.observations.critic = ScanFirstCriticCfg()
