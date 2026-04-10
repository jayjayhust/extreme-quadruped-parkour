# Environment Configuration and Setup

<cite>
**Referenced Files in This Document**
- [go2_env_cfg.py](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py)
- [go2_env.py](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py)
- [rsl_rl_ppo_cfg.py](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py)
- [__init__.py](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py)
- [terrain_generator.py](file://source/isaaclab/isaaclab/terrains/terrain_generator.py)
- [configclass.py](file://source/isaaclab/isaaclab/utils/configclass.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
This document explains the Go2 Environment Configuration and Setup system used for quadruped parkour and locomotion research. It focuses on:
- Environment configuration classes Go2FlatEnvCfg and Go2RoughEnvCfg and their roles in the ablation study framework
- Terrain generation parameters, reward function scaling, sensor integration, and curriculum learning settings
- Environment registration via Gym and Gymnasium, and the Gym-compatible environment setup
- Agent configuration system using PPO hyperparameters, neural network architectures, and training parameters
- Practical examples for different terrain types, reward customization, and ablation setups
- Parameter validation and default value handling mechanisms

## Project Structure
The Go2 environment is organized under the isaaclab_tasks package with three primary modules:
- Environment configuration: defines environment parameters and reward terms
- Environment runtime: implements the Gymnasium-compatible RL environment
- Agent configuration: defines PPO runner and policy configurations for training

```mermaid
graph TB
subgraph "Go2 Task Package"
CFG["go2_env_cfg.py<br/>Configurations"]
ENV["go2_env.py<br/>Gym Env Implementation"]
AGENTS["agents/rsl_rl_ppo_cfg.py<br/>Agent Runner Configs"]
REG["__init__.py<br/>Gym Registration"]
end
CFG --> ENV
AGENTS --> ENV
REG --> ENV
```

**Diagram sources**
- [go2_env_cfg.py:70-170](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L70-L170)
- [go2_env.py:20-60](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L20-L60)
- [rsl_rl_ppo_cfg.py:44-112](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py#L44-L112)
- [__init__.py:18-47](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py#L18-L47)

**Section sources**
- [go2_env_cfg.py:70-170](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L70-L170)
- [go2_env.py:20-60](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L20-L60)
- [rsl_rl_ppo_cfg.py:44-112](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py#L44-L112)
- [__init__.py:18-47](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py#L18-L47)

## Core Components
- Go2FlatEnvCfg: Base configuration for flat terrain with minimal proprioceptive inputs and a simple reward function. Suitable for basic locomotion and baseline training.
- Go2RoughEnvCfg: Enhanced configuration for rough, procedurally generated terrain with a height scanner (ray caster) providing dense spatial observations. Includes curriculum learning and advanced reward terms tuned for parkour-like challenges.
- Go2RoughPlayEnvCfg: Evaluation variant that disables curriculum and sets fixed commands for deterministic playback.
- Ablation variants (Abl1, Abl2.5, Abl3.5, Abl4.0, Abl7.0): Specialized subclasses that remove or alter sensor fusion and encoder pathways to isolate the contribution of perception to policy performance.
- Agent runner configurations: PPO runner settings and policy architectures tailored to the Go2 task, including ablation-specific policies.

Key configuration parameters:
- Observation spaces: proprioceptive (prop) + optional scan (187 rays) for policy/critic
- Reward scales: configurable per task and terrain difficulty
- Sensors: contact sensors and a height scanner (ray caster) for terrain-aware locomotion
- Curriculum: terrain difficulty progression and command sampling modes

**Section sources**
- [go2_env_cfg.py:70-170](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L70-L170)
- [go2_env_cfg.py:172-314](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L172-L314)
- [go2_env_cfg.py:316-353](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L316-L353)
- [go2_env.py:293-355](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L293-L355)
- [rsl_rl_ppo_cfg.py:44-155](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py#L44-L155)

## Architecture Overview
The environment integrates configuration-driven behavior with a Gymnasium-compatible interface. The configuration classes define the environment’s dynamics, sensors, rewards, and curriculum. The environment runtime constructs the scene, applies actions, computes observations and rewards, and manages resets and curriculum updates.

```mermaid
sequenceDiagram
participant User as "User Script"
participant Gym as "Gym Registry (__init__.py)"
participant Env as "Go2Env (go2_env.py)"
participant Cfg as "Go2EnvCfg (go2_env_cfg.py)"
participant Agent as "RSL-RL PPO Runner (rsl_rl_ppo_cfg.py)"
User->>Gym : gym.make("Go2-Rough-Direct-v0")
Gym->>Env : construct(cfg_entry_point, rsl_rl_cfg_entry_point)
Env->>Cfg : load configuration (flat/rough/ablation)
Env->>Env : _setup_scene(), instantiate robot, sensors
User->>Env : step(action)
Env->>Env : _pre_physics_step(), _apply_action()
Env->>Env : _get_observations(), _get_rewards()
Env-->>User : (obs, reward, terminated, truncated, info)
User->>Agent : train(runner_cfg, policy_cfg)
Agent-->>User : metrics/logs
```

**Diagram sources**
- [__init__.py:18-47](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py#L18-L47)
- [go2_env.py:20-60](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L20-L60)
- [go2_env_cfg.py:70-170](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L70-L170)
- [rsl_rl_ppo_cfg.py:44-112](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py#L44-L112)

## Detailed Component Analysis

### Environment Configuration Classes
- Go2FlatEnvCfg
  - Proprioceptive-only observations (no scan)
  - Flat terrain with plane ground
  - Basic reward terms for velocity tracking and stabilization
  - Command sampling modes and curriculum toggle
- Go2RoughEnvCfg
  - Adds a height scanner (ray caster) for dense terrain perception
  - Procedurally generated rough terrain with curriculum
  - Extended reward terms for parkour-relevant behaviors
  - Heading command mode and fixed command overrides for parkour-like training
- Play configuration
  - Disables curriculum and sets fixed commands for evaluation
- Ablation configurations
  - Abl1: removes scan from policy
  - Abl2.5: scans first in policy/critic
  - Abl3.5–Abl7.0: variations in scan encoding and privilege observation encoding

```mermaid
classDiagram
class DirectRLEnvCfg
class Go2FlatEnvCfg {
+float episode_length_s
+int decimation
+float action_scale
+int action_space
+int observation_space
+int state_space
+int num_prop_obs
+int num_priv_obs
+int num_scan_obs
+bool use_scan_in_policy
+bool use_scan_in_critic
+bool scan_first_in_policy
+bool scan_first_in_critic
+SimulationCfg sim
+TerrainImporterCfg terrain
+ArticulationCfg robot
+ContactSensorCfg contact_sensor
+dict reward scales
+str command_mode
+tuple fixed_command
+bool use_curriculum
+bool heading_command
+tuple command_heading_range
+tuple command_yaw_range
}
class Go2RoughEnvCfg {
+str gap_subterrain_key
+str hurdle_subterrain_key
+float gap_spawn_offset
+int observation_space
+int state_space
+int num_scan_obs
+bool use_scan_in_policy
+bool use_scan_in_critic
+SimulationCfg sim
+TerrainImporterCfg terrain
+RayCasterCfg height_scanner
+dict reward scales
+str command_mode
+bool use_curriculum
+bool heading_command
+tuple command_heading_range
+tuple command_yaw_range
}
class Go2RoughPlayEnvCfg {
+bool use_curriculum
+str command_mode
+tuple fixed_command
}
class Go2RoughAbl1EnvCfg {
+bool use_scan_in_policy
}
class Go2RoughAbl2_5EnvCfg {
+bool scan_first_in_policy
+bool scan_first_in_critic
}
Go2FlatEnvCfg --|> DirectRLEnvCfg
Go2RoughEnvCfg --|> Go2FlatEnvCfg
Go2RoughPlayEnvCfg --|> Go2RoughEnvCfg
Go2RoughAbl1EnvCfg --|> Go2RoughEnvCfg
Go2RoughAbl2_5EnvCfg --|> Go2RoughEnvCfg
```

**Diagram sources**
- [go2_env_cfg.py:70-170](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L70-L170)
- [go2_env_cfg.py:172-314](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L172-L314)
- [go2_env_cfg.py:316-353](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L316-L353)

**Section sources**
- [go2_env_cfg.py:70-170](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L70-L170)
- [go2_env_cfg.py:172-314](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L172-L314)
- [go2_env_cfg.py:316-353](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L316-L353)

### Environment Runtime and Sensor Integration
- Scene setup: instantiates robot, contact sensor, and optionally the height scanner for rough terrain
- Action pipeline: scales actions and applies joint position targets
- Observations:
  - Policy input: prop + optional scan (order controlled by scan_first flags)
  - Critic input: prop + privileged obs (mass, COM, friction, PD gains) + optional scan
- Rewards: composite of velocity tracking, stabilization, contact penalties, and terrain-aware terms
- Curriculum: updates terrain difficulty based on achieved distance and command speed

```mermaid
flowchart TD
Start(["Reset/Step"]) --> Actions["Scale and Apply Actions"]
Actions --> Observe["Compute Observations"]
Observe --> PolicyObs["Policy Obs: prop + optional scan"]
Observe --> CriticObs["Critic Obs: prop + priv + optional scan"]
Actions --> Dynamics["Physics Step"]
Dynamics --> Rewards["Compute Rewards"]
Rewards --> DoneCheck{"Termination/Timeout?"}
DoneCheck --> |Yes| Reset["Reset Environments"]
DoneCheck --> |No| Continue["Continue Episode"]
Reset --> Curriculum["Update Curriculum (Rough)"]
Curriculum --> Start
```

**Diagram sources**
- [go2_env.py:233-274](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L233-L274)
- [go2_env.py:293-355](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L293-L355)
- [go2_env.py:467-535](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L467-L535)

**Section sources**
- [go2_env.py:212-232](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L212-L232)
- [go2_env.py:293-355](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L293-L355)
- [go2_env.py:467-535](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L467-L535)

### Environment Registration and Gym-Compatible Setup
- Registers multiple Gym environments:
  - Flat: Go2-Direct-v0
  - Rough: Go2-Rough-Direct-v0 and Abl variants
  - Play: Go2-Rough-Direct-Play-v0 and Abl Play variants
- Each registration passes environment and agent configuration entry points to the environment constructor

```mermaid
sequenceDiagram
participant Reg as "__init__.py"
participant Gym as "Gym Registry"
participant Env as "Go2Env"
Reg->>Gym : gym.register(id, entry_point, kwargs)
Note over Reg,Gym : kwargs include env_cfg_entry_point and rsl_rl_cfg_entry_point
Gym->>Env : construct(cfg_entry_point, rsl_rl_cfg_entry_point)
Env-->>Gym : ready for training/inference
```

**Diagram sources**
- [__init__.py:18-47](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py#L18-L47)
- [__init__.py:49-147](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py#L49-L147)

**Section sources**
- [__init__.py:18-47](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py#L18-L47)
- [__init__.py:49-147](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py#L49-L147)

### Agent Configuration System (PPO)
- Runner configurations:
  - Go2FlatPPORunnerCfg: baseline PPO with proprioceptive-only policy
  - Go2RoughPPORunnerCfg: PPO with scan observations and higher learning rate
  - Abl variants:
    - Abl1: policy without scan
    - Abl2.5: policy without scan encoder (ActorCritic)
    - Abl3.5–Abl7.0: policy with scan encoder and/or privileged encoder modifications
- Policy architecture:
  - Actor/Critic hidden layers and activation
  - Scan encoder dimensions and privilege encoder dimensions
  - Noise initialization and KL divergence targeting

```mermaid
classDiagram
class RslRlOnPolicyRunnerCfg
class RslRlPpoActorCriticCfg {
+str class_name
+float init_noise_std
+str noise_std_type
+int[] actor_hidden_dims
+int[] critic_hidden_dims
+str activation
+int num_prop_obs
+int num_scan_obs
+int[] scan_encoder_dims
+int[] priv_obs_encoder_dims
}
class RslRlPpoAlgorithmCfg {
+float value_loss_coef
+bool use_clipped_value_loss
+float clip_param
+float entropy_coef
+int num_learning_epochs
+int num_mini_batches
+float learning_rate
+str schedule
+float gamma
+float lam
+float desired_kl
+float max_grad_norm
}
class Go2FlatPPORunnerCfg
class Go2RoughPPORunnerCfg
class Go2RoughAbl1PPORunnerCfg
class Go2RoughAbl2_5PPORunnerCfg
class Go2RoughAbl3_5PPORunnerCfg
class Go2RoughAbl4_0PPORunnerCfg
class Go2RoughAbl7_0PPORunnerCfg
Go2FlatPPORunnerCfg --> RslRlOnPolicyRunnerCfg
Go2RoughPPORunnerCfg --> RslRlOnPolicyRunnerCfg
Go2RoughAbl1PPORunnerCfg --> Go2RoughPPORunnerCfg
Go2RoughAbl2_5PPORunnerCfg --> Go2RoughPPORunnerCfg
Go2RoughAbl3_5PPORunnerCfg --> Go2RoughPPORunnerCfg
Go2RoughAbl4_0PPORunnerCfg --> Go2RoughPPORunnerCfg
Go2RoughAbl7_0PPORunnerCfg --> Go2RoughPPORunnerCfg
RslRlPpoActorCriticCfg <-- Go2FlatPPORunnerCfg
RslRlPpoActorCriticCfg <-- Go2RoughPPORunnerCfg
RslRlPpoActorCriticCfg <-- Go2RoughAbl1PPORunnerCfg
RslRlPpoActorCriticCfg <-- Go2RoughAbl2_5PPORunnerCfg
RslRlPpoActorCriticCfg <-- Go2RoughAbl3_5PPORunnerCfg
RslRlPpoActorCriticCfg <-- Go2RoughAbl4_0PPORunnerCfg
RslRlPpoActorCriticCfg <-- Go2RoughAbl7_0PPORunnerCfg
RslRlPpoAlgorithmCfg <-- Go2FlatPPORunnerCfg
RslRlPpoAlgorithmCfg <-- Go2RoughPPORunnerCfg
```

**Diagram sources**
- [rsl_rl_ppo_cfg.py:44-155](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py#L44-L155)

**Section sources**
- [rsl_rl_ppo_cfg.py:44-155](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py#L44-L155)

### Practical Examples

- Flat terrain baseline
  - Use Go2-Direct-v0 with Go2FlatEnvCfg and Go2FlatPPORunnerCfg
  - Ideal for initial policy learning and debugging

- Rough terrain parkour
  - Use Go2-Rough-Direct-v0 with Go2RoughEnvCfg and Go2RoughPPORunnerCfg
  - Enables curriculum learning and heading command modes

- Ablation studies
  - Abl1: remove scan from policy (Go2-Rough-Direct-Abl1-v0)
  - Abl2.5: remove scan encoder (Go2-Rough-Direct-Abl2_5-v0)
  - Abl3.5: scan encoder for policy/critic (Go2-Rough-Direct-Abl3_5-v0)
  - Abl4.0: scan encoder for policy only (Go2-Rough-Direct-Abl4_0-v0)
  - Abl7.0: scan and privileged encoders (Go2-Rough-Direct-Abl7_0-v0)

- Reward customization
  - Adjust reward scales in the environment configuration classes (e.g., Go2RoughEnvCfg overrides)
  - Example scales for parkour-like behaviors are provided in the rough configuration

- Curriculum learning
  - Enable curriculum via use_curriculum flag
  - Configure command_mode and heading_command for parkour-like training

**Section sources**
- [__init__.py:18-47](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py#L18-L47)
- [__init__.py:49-147](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py#L49-L147)
- [go2_env_cfg.py:172-314](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L172-L314)
- [go2_env_cfg.py:279-297](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L279-L297)

### Relationship Between Configuration and Implementation
- Configuration drives environment behavior:
  - Observation space composition (prop + scan)
  - Sensor instantiation (contact sensor, height scanner)
  - Reward computation and logging
  - Curriculum updates and command sampling
- Implementation validates and applies configuration:
  - Post-init recalculation of observation/state spaces
  - Conditional sensor creation for rough terrain
  - Dynamic command selection and heading control

```mermaid
graph LR
Cfg["Go2EnvCfg (go2_env_cfg.py)"] --> Impl["_setup_scene(), _get_observations(), _get_rewards()"]
Impl --> Obs["Observations"]
Impl --> Rew["Rewards"]
Impl --> Cur["Curriculum Updates"]
```

**Diagram sources**
- [go2_env_cfg.py:311-313](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L311-L313)
- [go2_env.py:212-232](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L212-L232)
- [go2_env.py:293-355](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L293-L355)
- [go2_env.py:473-535](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L473-L535)

**Section sources**
- [go2_env_cfg.py:311-313](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L311-L313)
- [go2_env.py:212-232](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L212-L232)
- [go2_env.py:293-355](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L293-L355)
- [go2_env.py:473-535](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L473-L535)

## Dependency Analysis
- Environment configuration depends on:
  - DirectRLEnvCfg base class
  - Simulation and terrain configuration classes
  - Asset and sensor configuration classes
- Environment runtime depends on:
  - Configuration classes for behavior
  - Sensor classes for observations
  - Reward computation logic
- Agent runner depends on:
  - PPO runner and algorithm configurations
  - Policy configuration with optional scan encoders

```mermaid
graph TB
EnvCfg["go2_env_cfg.py"] --> BaseCfg["DirectRLEnvCfg"]
EnvCfg --> Sim["SimulationCfg"]
EnvCfg --> Terrain["TerrainImporterCfg"]
EnvCfg --> Assets["ArticulationCfg"]
EnvCfg --> Sensors["ContactSensorCfg / RayCasterCfg"]
EnvImpl["go2_env.py"] --> EnvCfg
EnvImpl --> Sensors
AgentCfg["rsl_rl_ppo_cfg.py"] --> Runner["RslRlOnPolicyRunnerCfg"]
AgentCfg --> Policy["RslRlPpoActorCriticCfg"]
AgentCfg --> Algo["RslRlPpoAlgorithmCfg"]
Reg["__init__.py"] --> EnvImpl
Reg --> AgentCfg
```

**Diagram sources**
- [go2_env_cfg.py:70-170](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L70-L170)
- [go2_env.py:20-60](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L20-L60)
- [rsl_rl_ppo_cfg.py:44-155](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py#L44-L155)
- [__init__.py:18-47](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py#L18-L47)

**Section sources**
- [go2_env_cfg.py:70-170](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L70-L170)
- [go2_env.py:20-60](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L20-L60)
- [rsl_rl_ppo_cfg.py:44-155](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py#L44-L155)
- [__init__.py:18-47](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py#L18-L47)

## Performance Considerations
- Observation composition:
  - Adding scan observations increases policy/critic input size; tune scan resolution and encoder dimensions accordingly
- Curriculum and terrain generation:
  - Larger terrain grids and diverse sub-terrains improve generalization but increase compute
- Simulation settings:
  - GPU patch counts and solver iterations impact stability and speed
- Learning rates and batch sizes:
  - Higher learning rates for rough terrain may require adjusted KL targets and gradient norms

## Troubleshooting Guide
- Missing type annotations or defaults:
  - The configuration system enforces type hints and default values; ensure all fields are annotated or initialized
- Unexpected observation sizes:
  - Verify use_scan_in_policy/use_scan_in_critic flags and scan_first_* settings; post-init recalculations derive observation/state spaces
- Curriculum not updating:
  - Confirm use_curriculum is enabled and that terrain origins are available; check episode length and distance thresholds
- Sensor not appearing:
  - Height scanner is only instantiated for rough terrain configurations; ensure the environment uses Go2RoughEnvCfg or derived classes

**Section sources**
- [configclass.py:221-236](file://source/isaaclab/isaaclab/utils/configclass.py#L221-L236)
- [go2_env_cfg.py:311-313](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L311-L313)
- [go2_env.py:473-535](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L473-L535)
- [go2_env.py:212-232](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L212-L232)

## Conclusion
The Go2 Environment Configuration and Setup system provides a flexible, modular framework for quadruped locomotion and parkour research. Go2FlatEnvCfg offers a simple baseline, while Go2RoughEnvCfg enables advanced perception and curriculum learning. The Gym registration and agent runner configurations support reproducible ablation studies and scalable training. Proper configuration of sensors, rewards, and curriculum yields robust policies capable of navigating challenging terrains.