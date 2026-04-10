# Project Overview

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [go2_env_cfg.py](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py)
- [go2_env.py](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py)
- [rsl_rl_ppo_cfg.py](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py)
- [actor_critic_scan.py](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/actor_critic_scan.py)
- [__init__.py](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py)
- [train.py](file://scripts/reinforcement_learning/rsl_rl/train.py)
- [play.py](file://scripts/reinforcement_learning/rsl_rl/play.py)
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
This document presents the Extreme Quadruped Parkour project overview. The project consolidates five network ablation studies into a unified codebase for Unitree Go2 quadruped locomotion on extreme terrains. It systematically evaluates sensor fusion architecture choices via controlled ablations and reports findings on optimal observation pathways for policy and critic networks. The project builds on prior work in rough-terrain locomotion and parkour and provides a reproducible framework for training and evaluating policies under challenging conditions.

## Project Structure
The repository organizes the ablation studies around:
- Environment and task registration for five ablations
- Observation and reward pipeline tailored for rough terrain
- Policy and critic network configurations with optional scan and privileged observation encoders
- Training and playback scripts leveraging RSL-RL

```mermaid
graph TB
A["Task Registration<br/>Go2-Rough-Direct-*"] --> B["Environment Configurations<br/>go2_env_cfg.py"]
B --> C["Environment Implementation<br/>go2_env.py"]
C --> D["Observation Pipeline<br/>prop + scan + priv"]
D --> E["Policy/Critic Configurations<br/>rsl_rl_ppo_cfg.py"]
E --> F["Actor-Critic with Encoders<br/>actor_critic_scan.py"]
F --> G["Training Script<br/>train.py"]
F --> H["Playback Script<br/>play.py"]
```

**Diagram sources**
- [__init__.py:18-97](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py#L18-L97)
- [go2_env_cfg.py:334-353](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L334-L353)
- [go2_env.py:293-355](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L293-L355)
- [rsl_rl_ppo_cfg.py:115-155](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py#L115-L155)
- [actor_critic_scan.py:13-262](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/actor_critic_scan.py#L13-L262)
- [train.py:119-210](file://scripts/reinforcement_learning/rsl_rl/train.py#L119-L210)
- [play.py:94-154](file://scripts/reinforcement_learning/rsl_rl/play.py#L94-L154)

**Section sources**
- [README.md:44-50](file://README.md#L44-L50)
- [__init__.py:18-97](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py#L18-L97)

## Core Components
- Task IDs and ablation mapping: The project exposes five Gym tasks, each corresponding to a specific sensor fusion configuration for policy and critic inputs.
- Environment configuration: Defines observation spaces, terrain generation, reward scales, and curriculum behavior for rough-terrain training.
- Observation pipeline: Constructs per-environment observations from proprioceptive signals, a height-field scan, and privileged observations for the critic.
- Policy/Critic configuration: Provides ablation-specific settings for scan encoding and privileged observation encoding.
- Actor-critic with encoders: Implements optional encoders for scan and privileged observations, enabling flexible sensor fusion patterns.
- Training and playback: Scripts orchestrate training and evaluation with standardized logging and checkpointing.

**Section sources**
- [README.md:5-17](file://README.md#L5-L17)
- [go2_env_cfg.py:172-314](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L172-L314)
- [go2_env.py:293-355](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L293-L355)
- [rsl_rl_ppo_cfg.py:115-155](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py#L115-L155)
- [actor_critic_scan.py:13-262](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/actor_critic_scan.py#L13-L262)
- [train.py:119-210](file://scripts/reinforcement_learning/rsl_rl/train.py#L119-L210)
- [play.py:94-154](file://scripts/reinforcement_learning/rsl_rl/play.py#L94-L154)

## Architecture Overview
The system integrates environment configuration, observation construction, policy/critic definition, and training/evaluation loops. Observations are composed from:
- Proprioceptive observations (prop_obs)
- Height-field scan observations (scan_obs)
- Privileged observations (priv_obs) for the critic only

The ablations vary how these modalities are fused and whether encoders are applied to scan and/or privileged inputs.

```mermaid
graph TB
subgraph "Environment"
ECfg["Config<br/>go2_env_cfg.py"]
EImpl["Implementation<br/>go2_env.py"]
end
subgraph "Policy/Critic"
PCfg["Policy/Critic Config<br/>rsl_rl_ppo_cfg.py"]
Net["Actor-Critic with Encoders<br/>actor_critic_scan.py"]
end
subgraph "Execution"
Train["Training<br/>train.py"]
Play["Playback<br/>play.py"]
end
ECfg --> EImpl
EImpl --> PCfg
PCfg --> Net
Net --> Train
Net --> Play
```

**Diagram sources**
- [go2_env_cfg.py:172-314](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L172-L314)
- [go2_env.py:293-355](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L293-L355)
- [rsl_rl_ppo_cfg.py:115-155](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py#L115-L155)
- [actor_critic_scan.py:13-262](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/actor_critic_scan.py#L13-L262)
- [train.py:119-210](file://scripts/reinforcement_learning/rsl_rl/train.py#L119-L210)
- [play.py:94-154](file://scripts/reinforcement_learning/rsl_rl/play.py#L94-L154)

## Detailed Component Analysis

### Sensor Fusion and Observation Pipeline
- Proprioceptive observations (prop_obs): 52D including joint positions/velocities, projected gravity, base linear/angular velocities, commanded values, recent actions, and foot contacts.
- Privileged observations (priv_obs): 29D including mass, center of mass, friction coefficients, and PD gain scales; used for the critic only.
- Scan observations (scan_obs): 187D height grid representing terrain elevation around the robot.
- Observation composition:
  - Policy input: prop_obs optionally concatenated with scan representation (raw or encoded).
  - Critic input: prop_obs + priv_obs + scan representation (raw or encoded), with optional scan-first ordering.

```mermaid
flowchart TD
Start(["Observation Build"]) --> Collect["Collect prop_obs<br/>52D"]
Collect --> ScanSel{"Use scan in policy?"}
ScanSel --> |Yes| ScanRaw["Height scan<br/>187D"]
ScanSel --> |No| SkipScan["Skip scan for policy"]
ScanRaw --> EncodeA{"Encode scan for policy?"}
EncodeA --> |Yes| ZScanA["Actor scan latent<br/>dim from encoder"]
EncodeA --> |No| RawScanA["Use raw scan for policy"]
ZScanA --> PolicyObs["Concatenate prop + scan latent"]
RawScanA --> PolicyObs
SkipScan --> PolicyObs
PolicyObs --> CriticSel{"Use scan in critic?"}
CriticSel --> |Yes| ScanC["Height scan<br/>187D"]
CriticSel --> |No| SkipScanC["Skip scan for critic"]
ScanC --> EncodeC{"Encode scan for critic?"}
EncodeC --> |Yes| ZScanC["Critic scan latent"]
EncodeC --> |No| RawScanC["Use raw scan for critic"]
ZScanC --> CriticObs["Concatenate prop + priv + scan latent"]
RawScanC --> CriticObs
SkipScanC --> CriticObs
CriticObs --> End(["Done"])
```

**Diagram sources**
- [go2_env.py:293-355](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L293-L355)
- [go2_env_cfg.py:172-314](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L172-L314)

**Section sources**
- [README.md:51-67](file://README.md#L51-L67)
- [go2_env.py:293-355](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L293-L355)
- [go2_env_cfg.py:172-314](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L172-L314)

### Ablation Study Methodology and Network Architectures
The project defines five ablations that vary how scan and privileged observations are incorporated:
- Abl 1: Actor uses prop_obs only; Critic uses prop_obs + priv_obs + raw scan.
- Abl 2.5: Both policy and critic use prop_obs + raw scan; scan-first ordering is enabled.
- Abl 3.5: Both policy and critic use prop_obs + scan encoding.
- Abl 4.0: Actor uses prop_obs + scan encoding; Critic uses prop_obs + priv_obs + raw scan.
- Abl 7.0: Actor uses prop_obs + scan encoding; Critic uses prop_obs + priv_obs encoding + scan encoding.

```mermaid
classDiagram
class ActorCriticScan {
+bool is_recurrent
+int num_actor_obs
+int num_critic_obs
+int num_prop
+int num_actor_scan
+int num_critic_scan
+int num_priv
+bool encode_scan_for_critic
+forward(observations) -> actions
+evaluate(critic_observations) -> value
}
class PolicyConfigs {
+int num_actor_scan_obs
+int num_critic_scan_obs
+list scan_encoder_dims
+list actor_scan_encoder_dims
+list critic_scan_encoder_dims
+bool encode_scan_for_critic
+list priv_obs_encoder_dims
+list priv_encoder_dims
}
ActorCriticScan --> PolicyConfigs : "configured by"
```

**Diagram sources**
- [actor_critic_scan.py:13-262](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/actor_critic_scan.py#L13-L262)
- [rsl_rl_ppo_cfg.py:11-41](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py#L11-L41)

**Section sources**
- [README.md:12-17](file://README.md#L12-L17)
- [rsl_rl_ppo_cfg.py:115-155](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py#L115-L155)
- [actor_critic_scan.py:13-262](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/actor_critic_scan.py#L13-L262)

### Practical Ablation Workflow
- Training: Select a task ID and run the training script with desired number of environments.
- Playback: Load a checkpoint and run the playback script to evaluate a trained policy.

```mermaid
sequenceDiagram
participant User as "User"
participant Train as "train.py"
participant Env as "Go2Env"
participant Runner as "RSL-RL OnPolicyRunner"
participant Policy as "ActorCriticScan"
User->>Train : Launch with task ID and num_envs
Train->>Env : Create Gym environment
Train->>Runner : Initialize with agent_cfg
Runner->>Policy : Instantiate policy with ablation settings
loop Training iterations
Runner->>Env : Step and collect obs/reward
Runner->>Policy : Act and evaluate
Runner->>Runner : Update policy
end
Runner-->>User : Save logs/checkpoints
```

**Diagram sources**
- [train.py:119-210](file://scripts/reinforcement_learning/rsl_rl/train.py#L119-L210)
- [go2_env.py:293-355](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env.py#L293-L355)
- [actor_critic_scan.py:13-262](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/actor_critic_scan.py#L13-L262)

**Section sources**
- [README.md:120-172](file://README.md#L120-L172)
- [train.py:119-210](file://scripts/reinforcement_learning/rsl_rl/train.py#L119-L210)
- [play.py:94-154](file://scripts/reinforcement_learning/rsl_rl/play.py#L94-L154)

### Research Contributions and Findings
- The ablations demonstrate the importance of scan encoding for both policy and critic.
- Using raw scan in the critic leads to noisy value estimates and degraded performance.
- Privileged observation encoding for the critic can cause overfitting to constant parameters.
- Abl 3.5 (scan encoding for both policy and critic) achieves the best mean reward and velocity tracking and is most stable on the hardest terrains.

```mermaid
flowchart TD
A["Abl 1<br/>blind walking"] --> Fail["Failures due to no scan access"]
B["Abl 2.5<br/>raw scan everywhere"] --> Issues["Feature extraction issues"]
C["Abl 3.5<br/>scan encoding both"] --> Best["Best performance"]
D["Abl 4.0<br/>raw scan in critic"] --> Degrade["Noisy value estimation"]
E["Abl 7.0<br/>priv obs encoding"] --> Overfit["Constants overfitting"]
Fail --> Conclude["Use scan encoding for both actor and critic<br/>Avoid priv_obs encoding for critic"]
Issues --> Conclude
Best --> Conclude
Degrade --> Conclude
Overfit --> Conclude
```

**Diagram sources**
- [README.md:109-119](file://README.md#L109-L119)

**Section sources**
- [README.md:109-119](file://README.md#L109-L119)

## Dependency Analysis
- Task registration maps Gym IDs to environment configurations and agent configurations.
- Environment configuration controls observation dimensions, terrain generation, and curriculum behavior.
- Agent configuration selects the policy class and encoder settings per ablation.
- Actor-critic module implements the neural network with optional encoders.

```mermaid
graph LR
Reg["Task Registration<br/>__init__.py"] --> EnvCfg["Env Config<br/>go2_env_cfg.py"]
EnvCfg --> EnvImpl["Env Impl<br/>go2_env.py"]
EnvImpl --> AgentCfg["Agent Config<br/>rsl_rl_ppo_cfg.py"]
AgentCfg --> Net["ActorCriticScan<br/>actor_critic_scan.py"]
```

**Diagram sources**
- [__init__.py:18-97](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py#L18-L97)
- [go2_env_cfg.py:172-314](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L172-L314)
- [rsl_rl_ppo_cfg.py:115-155](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py#L115-L155)
- [actor_critic_scan.py:13-262](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/actor_critic_scan.py#L13-L262)

**Section sources**
- [__init__.py:18-97](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/__init__.py#L18-L97)
- [go2_env_cfg.py:172-314](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/go2_env_cfg.py#L172-L314)
- [rsl_rl_ppo_cfg.py:115-155](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py#L115-L155)
- [actor_critic_scan.py:13-262](file://source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/actor_critic_scan.py#L13-L262)

## Performance Considerations
- Large-scale training: The setup supports 4096 environments; adjust --num_envs if memory or compute is constrained.
- Rendering and headless modes: Use headless mode for faster training without visualization.
- Encoder choice impacts convergence stability and value estimation accuracy; favor scan encoding for both actor and critic.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
- Environment setup: Ensure the Isaac Lab version and dependencies match the documented prerequisites.
- GPU availability: Training is recommended on GPU; reduce --num_envs if running low on memory.
- Curriculum and commands: Adjust max_init_terrain_level and terrain parameters for targeted difficulty.
- Checkpoint loading: Use --load_run and --checkpoint with the playback script to evaluate specific runs.

**Section sources**
- [README.md:30-42](file://README.md#L30-L42)
- [README.md:165-172](file://README.md#L165-L172)

## Conclusion
The Extreme Quadruped Parkour project provides a unified, reproducible framework for evaluating sensor fusion strategies in rough-terrain quadruped locomotion. The five ablations reveal that scan encoding benefits both policy and critic, while raw scan in the critic and privileged observation encoding for the critic degrade performance. These findings inform practical guidelines for perception-action pipelines in challenging environments.