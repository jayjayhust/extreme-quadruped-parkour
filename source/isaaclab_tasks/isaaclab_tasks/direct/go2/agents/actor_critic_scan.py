# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import torch
import torch.nn as nn
from torch.distributions import Normal

from rsl_rl.utils import resolve_nn_activation


class ActorCriticScan(nn.Module):
    """Actor-Critic with a shared scan encoder.

    - Actor input: prop_obs + "scan_latent(encoded from raw scan)"
    - Critic input: prop_obs + priv_obs + "scan_latent(encoded from raw scan)"
    """

    is_recurrent = False

    def __init__(
        self,
        num_actor_obs: int,
        num_critic_obs: int,
        num_actions: int,
        actor_hidden_dims=None,
        critic_hidden_dims=None,
        scan_encoder_dims=None,
        num_prop_obs: int = 52,
        num_scan_obs: int = 187,
        activation: str = "elu",
        init_noise_std: float = 1.0,
        noise_std_type: str = "scalar",
        **kwargs,
    ):
        if kwargs:
            print(
                "ActorCriticScan.__init__ ignored unexpected arguments: "
                + str([key for key in kwargs.keys()])
            )
        super().__init__()
        activation = resolve_nn_activation(activation)

        self.num_prop = num_prop_obs
        self.num_scan = max(0, num_scan_obs)
        self.num_priv = num_critic_obs - self.num_prop - self.num_scan
        if self.num_priv < 0:
            raise ValueError(
                f"Invalid critic obs split: num_critic_obs={num_critic_obs}, "
                f"num_prop={self.num_prop}, num_scan={self.num_scan}"
            )

        # scan encoder (shared by actor & critic)
        self.scan_latent_dim = 0
        if self.num_scan > 0 and scan_encoder_dims is not None and len(scan_encoder_dims) > 0:
            layers = []
            in_dim = self.num_scan
            for i, out_dim in enumerate(scan_encoder_dims):
                layers.append(nn.Linear(in_dim, out_dim))
                if i == len(scan_encoder_dims) - 1:
                    layers.append(nn.Tanh())
                else:
                    layers.append(activation)
                in_dim = out_dim
            self.scan_encoder = nn.Sequential(*layers)
            self.scan_latent_dim = scan_encoder_dims[-1]
        else:
            self.scan_encoder = None
            self.scan_latent_dim = self.num_scan

        # default hidden dims
        actor_hidden_dims = actor_hidden_dims or [256, 256, 256]
        critic_hidden_dims = critic_hidden_dims or [256, 256, 256]

        # actor/critic input dims after scan encoding
        actor_input_dim = (
            self.num_prop + self.scan_latent_dim if self.num_scan > 0 else num_actor_obs
        )
        critic_input_dim = (
            self.num_prop + self.num_priv + self.scan_latent_dim
            if self.num_scan > 0
            else num_critic_obs
        )

        # Actor MLP
        actor_layers = [nn.Linear(actor_input_dim, actor_hidden_dims[0]), activation]
        for layer_index in range(len(actor_hidden_dims)):
            if layer_index == len(actor_hidden_dims) - 1:
                actor_layers.append(nn.Linear(actor_hidden_dims[layer_index], num_actions))
            else:
                actor_layers.append(nn.Linear(actor_hidden_dims[layer_index], actor_hidden_dims[layer_index + 1]))
                actor_layers.append(activation)
        self.actor = nn.Sequential(*actor_layers)

        # Critic MLP
        critic_layers = [nn.Linear(critic_input_dim, critic_hidden_dims[0]), activation]
        for layer_index in range(len(critic_hidden_dims)):
            if layer_index == len(critic_hidden_dims) - 1:
                critic_layers.append(nn.Linear(critic_hidden_dims[layer_index], 1))
            else:
                critic_layers.append(nn.Linear(critic_hidden_dims[layer_index], critic_hidden_dims[layer_index + 1]))
                critic_layers.append(activation)
        self.critic = nn.Sequential(*critic_layers)

        # Action noise
        self.noise_std_type = noise_std_type
        if self.noise_std_type == "scalar":
            self.std = nn.Parameter(init_noise_std * torch.ones(num_actions))
        elif self.noise_std_type == "log":
            self.log_std = nn.Parameter(torch.log(init_noise_std * torch.ones(num_actions)))
        else:
            raise ValueError(f"Unknown standard deviation type: {self.noise_std_type}. Should be 'scalar' or 'log'")

        self.distribution = None
        Normal.set_default_validate_args(False)

    @property
    def action_mean(self):
        return self.distribution.mean if self.distribution is not None else None

    @property
    def action_std(self):
        return self.distribution.stddev if self.distribution is not None else None

    @property
    def entropy(self):
        return self.distribution.entropy().sum(dim=-1) if self.distribution is not None else None

    def _encode_scan(self, scan: torch.Tensor) -> torch.Tensor:
        if self.scan_encoder is None:
            return scan
        return self.scan_encoder(scan)

    def _build_actor_input(self, observations: torch.Tensor) -> torch.Tensor:
        if self.num_scan <= 0:
            return observations
        obs_prop = observations[:, : self.num_prop]
        obs_scan = observations[:, self.num_prop : self.num_prop + self.num_scan] # policy obs 벡터에서 스캔 구간만 잘라내는 부분입니다. policy obs 순서는 prop(앞 52) || scan(뒤 187)이므로, 그 슬라이스로 raw scan을 떼어내
        z_scan = self._encode_scan(obs_scan)
        return torch.cat([obs_prop, z_scan], dim=-1)

    def _build_critic_input(self, critic_observations: torch.Tensor) -> torch.Tensor:
        if self.num_scan <= 0:
            return critic_observations
        obs_prop = critic_observations[:, : self.num_prop]
        obs_priv = critic_observations[:, self.num_prop : self.num_prop + self.num_priv]
        obs_scan = critic_observations[
            :, self.num_prop + self.num_priv : self.num_prop + self.num_priv + self.num_scan
        ]
        z_scan = self._encode_scan(obs_scan)
        return torch.cat([obs_prop, obs_priv, z_scan], dim=-1)

    def update_distribution(self, observations):
        obs_enc = self._build_actor_input(observations)
        mean = self.actor(obs_enc)
        if self.noise_std_type == "scalar":
            std = self.std.expand_as(mean)
        elif self.noise_std_type == "log":
            std = torch.exp(self.log_std).expand_as(mean)
        else:
            raise ValueError(f"Unknown standard deviation type: {self.noise_std_type}. Should be 'scalar' or 'log'")
        self.distribution = Normal(mean, std)

    def act(self, observations, **kwargs):
        self.update_distribution(observations)
        return self.distribution.sample()

    def get_actions_log_prob(self, actions):
        return self.distribution.log_prob(actions).sum(dim=-1)

    def act_inference(self, observations):
        obs_enc = self._build_actor_input(observations)
        actions_mean = self.actor(obs_enc)
        return actions_mean

    def evaluate(self, critic_observations, **kwargs):
        critic_input = self._build_critic_input(critic_observations)
        value = self.critic(critic_input)
        return value

    def reset(self, dones=None):
        # stateless actor-critic; nothing to reset
        pass
