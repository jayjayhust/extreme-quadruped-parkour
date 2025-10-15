# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import gymnasium as gym
import torch

import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation
from isaaclab.envs import DirectRLEnv
from isaaclab.sensors import ContactSensor, RayCaster

from .go2_env_cfg import Go2FlatEnvCfg, Go2RoughEnvCfg


class Go2Env(DirectRLEnv):
    cfg: Go2FlatEnvCfg | Go2RoughEnvCfg

    def __init__(self, cfg: Go2FlatEnvCfg | Go2RoughEnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)

        # Joint position command (deviation from default joint positions)
        self._actions = torch.zeros(self.num_envs, gym.spaces.flatdim(self.single_action_space), device=self.device)
        self._previous_actions = torch.zeros(
            self.num_envs, gym.spaces.flatdim(self.single_action_space), device=self.device
        )

        # X/Y linear velocity and yaw angular velocity commands
        self._commands = torch.zeros(self.num_envs, 3, device=self.device)
        # Store command history and episode start poses for curriculum progression
        self._episode_commands = torch.zeros_like(self._commands)
        self._episode_start_pos = torch.zeros(self.num_envs, 3, device=self.device) # episode가 끝나는 시점에서의 로봇의 현재 위치와, episode 시작점 사이의 거리를 통해 episode내에서 로봇이 얼만큼 걸었나를 판별 -> 이 실제 이동한 거리값을 기준으로 커리큘럼 승급/강등 여부 판단

        # Logging
        self._episode_sums = {
            key: torch.zeros(self.num_envs, dtype=torch.float, device=self.device)
            for key in [
                "track_lin_vel_xy_exp",
                "track_ang_vel_z_exp",
                "lin_vel_z_l2",
                "ang_vel_xy_l2",
                "dof_torques_l2",
                "dof_acc_l2",
                "action_rate_l2",
                "feet_air_time",
                "undesired_contacts",
                "flat_orientation_l2",
                "base_height",
                "torques",
                "stop_penalty_lin",
                "stop_penalty_ang",
                "dof_close_to_default",
            ]
        }
        # Get specific body indices
        self._base_id, _ = self._contact_sensor.find_bodies("base")
        self._feet_ids, _ = self._contact_sensor.find_bodies(".*_foot")
        self._undesired_contact_body_ids, _ = self._contact_sensor.find_bodies(".*_thigh")

    def _setup_scene(self):
        self._robot = Articulation(self.cfg.robot)
        self.scene.articulations["robot"] = self._robot
        self._contact_sensor = ContactSensor(self.cfg.contact_sensor)
        self.scene.sensors["contact_sensor"] = self._contact_sensor
        if isinstance(self.cfg, Go2RoughEnvCfg):
            # we add a height scanner for perceptive locomotion --> scan dot data
            self._height_scanner = RayCaster(self.cfg.height_scanner)
            self.scene.sensors["height_scanner"] = self._height_scanner
        self.cfg.terrain.num_envs = self.scene.cfg.num_envs
        self.cfg.terrain.env_spacing = self.scene.cfg.env_spacing
        self._terrain = self.cfg.terrain.class_type(self.cfg.terrain)
        # clone and replicate
        self.scene.clone_environments(copy_from_source=False)
        # we need to explicitly filter collisions for CPU simulation
        if self.device == "cpu":
            self.scene.filter_collisions(global_prim_paths=[self.cfg.terrain.prim_path])
        # add lights
        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
        light_cfg.func("/World/Light", light_cfg)

    def _pre_physics_step(self, actions: torch.Tensor):
        self._actions = actions.clone()
        self._processed_actions = self.cfg.action_scale * self._actions + self._robot.data.default_joint_pos

    def _apply_action(self):
        self._robot.set_joint_position_target(self._processed_actions)

    def _get_observations(self) -> dict:
        self._previous_actions = self._actions.clone()
        height_data = None
        if isinstance(self.cfg, Go2RoughEnvCfg):
            height_data = (
                self._height_scanner.data.pos_w[:, 2].unsqueeze(1) - self._height_scanner.data.ray_hits_w[..., 2] - 0.5
            ).clip(-1.0, 1.0)
        obs = torch.cat(
            [
                tensor
                for tensor in (
                    self._robot.data.root_lin_vel_b,
                    self._robot.data.root_ang_vel_b,
                    self._robot.data.projected_gravity_b,
                    self._commands,
                    self._robot.data.joint_pos - self._robot.data.default_joint_pos,
                    self._robot.data.joint_vel,
                    height_data,
                    self._actions,
                )
                if tensor is not None
            ],
            dim=-1,
        )
        observations = {"policy": obs}
        return observations

    def _get_rewards(self) -> torch.Tensor:
        # linear velocity tracking
        lin_vel_error = torch.sum(torch.square(self._commands[:, :2] - self._robot.data.root_lin_vel_b[:, :2]), dim=1)
        lin_vel_error_mapped = torch.exp(-lin_vel_error / 0.25)
        # yaw rate tracking
        yaw_rate_error = torch.square(self._commands[:, 2] - self._robot.data.root_ang_vel_b[:, 2])
        yaw_rate_error_mapped = torch.exp(-yaw_rate_error / 0.25)
        # stop error
        lin_vel_norm_sq = torch.sum(torch.square(self._robot.data.root_lin_vel_b[:, :2]), dim=1)
        stop_penalty_lin = torch.exp(-2.0 * lin_vel_norm_sq)
        # angular velocity x/y
        ang_vel_error = torch.sum(torch.square(self._robot.data.root_ang_vel_b[:, :2]), dim=1)
        stop_penalty_ang = torch.exp(-2.0 * ang_vel_error)
        # z velocity tracking
        z_vel_error = torch.square(self._robot.data.root_lin_vel_b[:, 2])
        # joint torques
        joint_torques = torch.sum(torch.square(self._robot.data.applied_torque), dim=1)
        # joint acceleration
        joint_accel = torch.sum(torch.square(self._robot.data.joint_acc), dim=1)
        # action rate
        action_rate = torch.sum(torch.square(self._actions - self._previous_actions), dim=1)
        # feet air time
        first_contact = self._contact_sensor.compute_first_contact(self.step_dt)[:, self._feet_ids]
        last_air_time = self._contact_sensor.data.last_air_time[:, self._feet_ids]
        air_time = torch.sum((last_air_time - 0.5) * first_contact, dim=1) * (
            torch.norm(self._commands[:, :2], dim=1) > 0.1
        )
        # undesired contacts
        net_contact_forces = self._contact_sensor.data.net_forces_w_history
        is_contact = (
            torch.max(torch.norm(net_contact_forces[:, :, self._undesired_contact_body_ids], dim=-1), dim=1)[0] > 1.0
        )
        contacts = torch.sum(is_contact, dim=1)
        # flat orientation
        flat_orientation = torch.sum(torch.square(self._robot.data.projected_gravity_b[:, :2]), dim=1)

        # 직접 구현 한 reward function : base height #################################################################

        # Penalize base height away from target
        # base_height = torch.mean(self.base_pos[:, 2].unsqueeze(1) - self.measured_heights, dim=1)
        # rew_base_height = torch.square(base_height - self.cfg.rewards.base_height_target)
        
        base_height = torch.mean(self._robot.data.root_link_pose_w[:, 2].unsqueeze(1) , dim=1)
        # print(base_height[0])  # 대걸님이 debug용으로 넣은 코드인듯
        rew_base_height = torch.square(base_height - 0.3)
        rew_torque = torch.sum(self._robot.data.applied_torque, dim=1)
        rew_dof_close_to_default = torch.sum(
            torch.square(self._robot.data.joint_pos - self._robot.data.default_joint_pos), dim=1
        )
        ##########################################################################################################

        rewards = {
            "track_lin_vel_xy_exp": lin_vel_error_mapped * self.cfg.lin_vel_reward_scale * self.step_dt,
            "track_ang_vel_z_exp": yaw_rate_error_mapped * self.cfg.yaw_rate_reward_scale * self.step_dt,
            "lin_vel_z_l2": z_vel_error * self.cfg.z_vel_reward_scale * self.step_dt,
            "ang_vel_xy_l2": ang_vel_error * self.cfg.ang_vel_reward_scale * self.step_dt,
            "dof_torques_l2": joint_torques * self.cfg.joint_torque_reward_scale * self.step_dt,
            "dof_acc_l2": joint_accel * self.cfg.joint_accel_reward_scale * self.step_dt,
            "action_rate_l2": action_rate * self.cfg.action_rate_reward_scale * self.step_dt,
            "feet_air_time": air_time * self.cfg.feet_air_time_reward_scale * self.step_dt,
            "undesired_contacts": contacts * self.cfg.undesired_contact_reward_scale * self.step_dt,
            "flat_orientation_l2": flat_orientation * self.cfg.flat_orientation_reward_scale * self.step_dt,
            "base_height": rew_base_height * self.cfg.base_height_reward_scale * self.step_dt,
            "torques": rew_torque * self.cfg.torque_reward_scale * self.step_dt,
            "stop_penalty_lin": stop_penalty_lin * self.cfg.stop_penalty_reward_scale * self.step_dt,
            "stop_penalty_ang": stop_penalty_ang * self.cfg.stop_penalty_reward_scale * self.step_dt,
            "dof_close_to_default": (
                rew_dof_close_to_default * self.cfg.dof_close_to_default_reward_scale * self.step_dt
            ),
        }
        reward = torch.sum(torch.stack(list(rewards.values())), dim=0)
        # Logging
        for key, value in rewards.items():
            self._episode_sums[key] += value
        return reward

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        time_out = self.episode_length_buf >= self.max_episode_length - 1
        net_contact_forces = self._contact_sensor.data.net_forces_w_history
        died = torch.any(torch.max(torch.norm(net_contact_forces[:, :, self._base_id], dim=-1), dim=1)[0] > 1.0, dim=1)
        return died, time_out

    def _reset_idx(self, env_ids: torch.Tensor | None):
        if env_ids is None or len(env_ids) == self.num_envs:
            env_ids = self._robot._ALL_INDICES

        curriculum_log: dict[str, float] = dict()
        if (
            isinstance(self.cfg, Go2RoughEnvCfg)
            and getattr(self._terrain, "terrain_origins", None) is not None
        ):
            prev_mask = self.progress_buf[env_ids] > 0 # progress_buf는 0이면 막 리셋돼서 아직 한 발도 떼지 않은 에피소드 시작점 -> buffer updates at "(episode_length_buf += 1) at source/isaaclab/isaaclab/envs/direct_rl_env.py:368."
            if torch.any(prev_mask): # prev_mask에 최소한 한 요소라도 0보다 크면
                prev_env_ids = env_ids[prev_mask]
                current_pos = self._robot.data.root_link_pose_w[prev_env_ids, :3]
                start_pos = self._episode_start_pos[prev_env_ids]
                distance = torch.norm(current_pos[:, :2] - start_pos[:, :2], dim=1)
                terrain_length = self.cfg.terrain.terrain_generator.size[0] # 거친 지형 생성 설정에서 정의한 size 튜플의 첫 번째 값(= x 방향 길이)을 가져오는 줄. Rough terrain config에서는 size=(8.0, 8.0)으로 되어 있으니 size[0]은 각 서브 지형이 앞뒤로 8 m라는 뜻. 이 값을 써서 “지형 길이의 절반(=4 m)보다 더 멀리 걸었는가?”를 승급 조건으로.
                move_up = distance > (terrain_length * 0.5)
                prev_commands = self._episode_commands[prev_env_ids]
                command_speed = torch.norm(prev_commands[:, :2], dim=1)
                expected_distance = command_speed * self.max_episode_length_s # “명령을 끝까지 정확히 따라갔다면 이 에피소드에서 총 얼마를 이동했을 것이다”라는 이상적인 이동 거리를 계산하는 식.이 기대치의 절반 미만으로 실제 이동이 끝나면(move_down) 명령을 잘 수행하지 못했다고 보고 난이도를 낮추는 근거로 삼음.
                move_down = (distance < (expected_distance * 0.5)) & (~move_up)
                self._terrain.update_env_origins(prev_env_ids, move_up, move_down) # source/isaaclab/isaaclab/terrains/terrain_importer.py의 update_env_origins 함수 참고

                # 평균 지형 레벨 값을 Tensorboard 같은 로거에서 바로 볼 수 있게.
                curriculum_log["Curriculum/mean_terrain_level"] = torch.mean(
                    self._terrain.terrain_levels.float()
                ).item()

        self._robot.reset(env_ids)
        super()._reset_idx(env_ids)
        if len(env_ids) == self.num_envs:
            # Spread out the resets to avoid spikes in training when many environments reset at a similar time
            self.episode_length_buf[:] = torch.randint_like(self.episode_length_buf, high=int(self.max_episode_length))
        self._actions[env_ids] = 0.0
        self._previous_actions[env_ids] = 0.0
        # Sample new commands
        # 여기에서 command 처리할때 원래 크기는 envs, 3이라서 값이 이 샘플링을 통해 다 바뀌어버림.
        self._commands[env_ids] = torch.zeros_like(self._commands[env_ids]).uniform_(1.0, 1.0)
        
        # 각각 random sampling 구현 ###########################################################################
        num_resets = len(env_ids)


        ## THIS IS FOR TRAINING
        lin_x_range = [-1.0, 1.0]
        rand_x = (torch.rand(num_resets, 1, device=self.device) * (lin_x_range[1] - lin_x_range[0])) + lin_x_range[0]

        lin_y_range = [-1.0, 1.0]
        rand_y = (torch.rand(num_resets, 1, device=self.device) * (lin_y_range[1] - lin_y_range[0])) + lin_y_range[0]

        ang_vel_range = [-1.0, 1.0]
        rand_yaw = (torch.rand(num_resets, 1, device=self.device) * (ang_vel_range[1] - ang_vel_range[0])) + ang_vel_range[0]

        self._commands[env_ids] = torch.cat([rand_x, rand_y, rand_yaw], dim=1)
        self._episode_commands[env_ids] = self._commands[env_ids] # 지금 막 샘플링한 속도 명령(self._commands[env_ids])을 그대로 _episode_commands 버퍼에 복사해 두는 역할. 이렇게 저장해 둬야 에피소드가 끝날 때 “이 환경은 어떤 속도를 명령받았었나?”를 알 수 있고, 그 값을 이용해 기대 이동 거리(expected_distance)를 계산해서 커리큘럼 강등 여부를 판단

        # ## THIS IS FOR PLAYING
        # '''
        # # 고정된 x방향 속도로만 이동 (2.5 m/s)
        # fixed_x = torch.ones(num_resets, 1, device=self.device) * 2.5  # x방향 2.5 m/s
        # fixed_y = torch.zeros(num_resets, 1, device=self.device)       # y방향 0.0 m/s
        # fixed_yaw = torch.zeros(num_resets, 1, device=self.device)     # yaw 0.0 rad/s
        # self._commands[env_ids] = torch.cat([fixed_x, fixed_y, fixed_yaw], dim=1)   
        # '''
        # # 턴하면서 빠르게 이동
        # fixed_x = torch.ones(num_resets, 1,
        # device=self.device) * 3.0   # x방향 3.0 m/s
        # fixed_y = torch.zeros(num_resets, 1,
        # device=self.device)        # y방향 0.0 m/s
        # fixed_yaw = torch.ones(num_resets, 1,
        # device=self.device) * 2.0  # yaw 2.0 rad/s
        # self._commands[env_ids] = torch.cat([fixed_x,
        # fixed_y, fixed_yaw], dim=1)        
        
        ######################################################################################################
        
        # Reset robot state
        joint_pos = self._robot.data.default_joint_pos[env_ids]
        joint_vel = self._robot.data.default_joint_vel[env_ids]
        default_root_state = self._robot.data.default_root_state[env_ids]
        default_root_state[:, :3] += self._terrain.env_origins[env_ids]
        self._robot.write_root_pose_to_sim(default_root_state[:, :7], env_ids)
        self._robot.write_root_velocity_to_sim(default_root_state[:, 7:], env_ids)
        self._robot.write_joint_state_to_sim(joint_pos, joint_vel, None, env_ids)
        self._episode_start_pos[env_ids] = default_root_state[:, :3] # 이렇게 초기 좌표를 기록해 둬야 에피소드가 끝날 때 current_pos - start_pos로 실제 이동 거리를 계산할 수 있음.

        # Logging
        extras = dict()
        for key in self._episode_sums.keys():
            episodic_sum_avg = torch.mean(self._episode_sums[key][env_ids])
            extras["Episode_Reward/" + key] = episodic_sum_avg / self.max_episode_length_s
            self._episode_sums[key][env_ids] = 0.0
        self.extras["log"] = dict()
        self.extras["log"].update(extras)
        extras = dict()
        extras["Episode_Termination/base_contact"] = torch.count_nonzero(self.reset_terminated[env_ids]).item()
        extras["Episode_Termination/time_out"] = torch.count_nonzero(self.reset_time_outs[env_ids]).item()
        self.extras["log"].update(extras)
        if curriculum_log:
            self.extras["log"].update(curriculum_log)
