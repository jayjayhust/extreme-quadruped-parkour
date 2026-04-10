# Training and Experimentation

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [train.py](file://scripts/reinforcement_learning/rsl_rl/train.py)
- [cli_args.py](file://scripts/reinforcement_learning/rsl_rl/cli_args.py)
- [random_agent.py](file://scripts/environments/random_agent.py)
- [zero_agent.py](file://scripts/environments/zero_agent.py)
- [tuner.py](file://scripts/reinforcement_learning/ray/tuner.py)
- [util.py](file://scripts/reinforcement_learning/ray/util.py)
- [submit_job.py](file://scripts/reinforcement_learning/ray/submit_job.py)
- [wrap_resources.py](file://scripts/reinforcement_learning/ray/wrap_resources.py)
- [vision_cfg.py](file://scripts/reinforcement_learning/ray/hyperparameter_tuning/vision_cfg.py)
- [benchmark_rlgames.py](file://scripts/benchmarks/benchmark_rlgames.py)
- [train.py](file://scripts/reinforcement_learning/rl_games/train.py)
- [curriculum_manager.py](file://source/isaaclab/isaaclab/managers/curriculum_manager.py)
- [manager_based_rl_env.py](file://source/isaaclab/isaaclab/envs/manager_based_rl_env.py)
- [manager_based_rl_env_cfg.py](file://source/isaaclab/isaaclab/envs/manager_based_rl_env_cfg.py)
- [go2_parkour/__init__.py](file://source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/go2_parkour/__init__.py)
- [rough_env_cfg.py](file://source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/go2_parkour/rough_env_cfg.py)
- [rsl_rl_ppo_cfg.py](file://source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/go2_parkour/agents/rsl_rl_ppo_cfg.py)
- [observations.py](file://source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/go2_parkour/mdp/observations.py)
</cite>

## Update Summary
**Changes Made**
- Added comprehensive documentation for manager-based training approaches alongside direct training methods
- Updated training examples to include both Go2-Parkour-Rough-v0 and Go2-Parkour-Rough-Abl3_5-v0 task IDs
- Enhanced environment configuration documentation with manager-based RL environment specifics
- Expanded practical training configuration examples to cover both direct and manager-based approaches
- Updated experiment management to include IO descriptor export capabilities for manager-based environments

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
10. [Appendices](#appendices)

## Introduction
This document explains the Training and Experimentation workflows used to support the ablation study methodology for five Go2 parkour network architectures. The framework now supports both direct and manager-based training approaches, providing enhanced flexibility and modularity for environment configuration and policy training. It covers environment initialization, policy training loops, evaluation procedures, experiment management (configuration, checkpoints, and result tracking), hyperparameter optimization, curriculum learning, performance benchmarking against baseline agents, distributed training infrastructure for 4096 environments, validation/testing with random and zero agents, and practical examples for configuration and result analysis.

## Project Structure
The repository organizes training and experimentation under:
- scripts/reinforcement_learning: framework-specific training scripts and Ray-based hyperparameter tuning
- scripts/environments: baseline agents for validation (random and zero actions)
- source/isaaclab_tasks: task definitions and ablation-specific environment configurations
- source/isaaclab: runtime components such as curriculum management and manager-based environment abstractions

```mermaid
graph TB
A["Training Entrypoints<br/>scripts/reinforcement_learning/*"] --> B["Framework Scripts<br/>RSL-RL, RL-Games, SB3, SKRL"]
A --> C["Ray Tuning<br/>tuner.py, util.py, submit_job.py"]
D["Environments<br/>scripts/environments/*"] --> E["Baselines<br/>Random Agent, Zero Agent"]
F["Task Configurations<br/>source/isaaclab_tasks/*"] --> G["Direct Envs<br/>Go2-Rough-Direct-*"]
F --> H["Manager-Based Envs<br/>Go2-Parkour-Rough-*"]
I["Manager Abstractions<br/>source/isaaclab/isaaclab/managers/*"] --> J["Command, Curriculum, Reward Managers"]
K["Environment Managers<br/>source/isaaclab/isaaclab/envs/*"] --> L["ManagerBasedRLEnv, Configs"]
```

**Section sources**
- [README.md:120-172](file://README.md#L120-L172)
- [go2_parkour/__init__.py:1-161](file://source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/go2_parkour/__init__.py#L1-L161)

## Core Components
- RSL-RL training pipeline: initializes the simulation app, constructs environment and runner, handles distributed training, logs parameters, and executes learning iterations.
- Manager-based environment system: provides modular MDP components (commands, observations, rewards, terminations, curriculum) with configurable ablation variants.
- Ray hyperparameter tuning: orchestrates distributed sweeps, manages resource placement, and monitors metrics via TensorBoard logs.
- Baseline agents: random and zero-action agents for sanity checks and ablation comparisons.
- Curriculum manager: computes and logs curriculum terms for adaptive difficulty.
- Benchmarking utilities: multi-GPU configuration and logging for performance comparisons.

**Section sources**
- [train.py:119-213](file://scripts/reinforcement_learning/rsl_rl/train.py#L119-L213)
- [manager_based_rl_env.py:110-133](file://source/isaaclab/isaaclab/envs/manager_based_rl_env.py#L110-L133)
- [tuner.py:66-160](file://scripts/reinforcement_learning/ray/tuner.py#L66-L160)
- [util.py:20-53](file://scripts/reinforcement_learning/ray/util.py#L20-L53)
- [random_agent.py:41-65](file://scripts/environments/random_agent.py#L41-L65)
- [zero_agent.py:41-65](file://scripts/environments/zero_agent.py#L41-L65)
- [curriculum_manager.py:100-203](file://source/isaaclab/isaaclab/managers/curriculum_manager.py#L100-L203)

## Architecture Overview
The training and experimentation architecture integrates framework-specific runners with unified environment abstractions, supporting both direct and manager-based training paradigms with optional Ray orchestration for distributed tuning.

```mermaid
sequenceDiagram
participant User as "User"
participant Launcher as "AppLauncher"
participant Env as "ManagerBasedRLEnv"
participant Runner as "RSL-RL Runner"
participant Managers as "MDP Managers"
participant TB as "TensorBoard Logs"
User->>Launcher : Launch training with task and args
Launcher->>Env : Create gym env (manager-based)
Env->>Managers : Initialize command, reward, termination managers
Managers-->>Env : Configure MDP components
Env-->>Runner : Vectorized env wrapper
Runner->>Runner : Initialize agent and logger
Runner->>Env : Reset and step loop
Runner->>TB : Write metrics periodically
Runner-->>User : Finalized policy and logs
```

**Diagram sources**
- [train.py:119-213](file://scripts/reinforcement_learning/rsl_rl/train.py#L119-L213)
- [manager_based_rl_env.py:110-133](file://source/isaaclab/isaaclab/envs/manager_based_rl_env.py#L110-L133)

**Section sources**
- [train.py:119-213](file://scripts/reinforcement_learning/rsl_rl/train.py#L119-L213)
- [manager_based_rl_env.py:110-133](file://source/isaaclab/isaaclab/envs/manager_based_rl_env.py#L110-L133)

## Detailed Component Analysis

### Manager-Based Training Pipeline
- Environment initialization: selects task from manager-based registry, applies CLI overrides, sets seeds/devices for deterministic runs.
- Manager system: loads modular components (commands, rewards, terminations, curriculum) with configurable ablation variants.
- Distributed training: adjusts device per local rank and seeds across ranks.
- Logging and checkpoints: dumps YAML/pickle configs, optionally exports IO descriptors, records videos, resumes from checkpoints.

```mermaid
flowchart TD
Start(["Start"]) --> Parse["Parse CLI and Hydra args"]
Parse --> Seed["Set env seed and device"]
Seed --> Dist{"Distributed?"}
Dist --> |Yes| Rank["Adjust device and seed per local rank"]
Dist --> |No| LoadMgrs["Load MDP managers"]
Rank --> LoadMgrs
LoadMgrs --> IO{"Export IO descriptors?"}
IO --> |Yes| Export["Export IO descriptors"]
IO --> |No| Wrap["Wrap env for RSL-RL"]
Export --> Wrap
Wrap --> Resume{"Resume from checkpoint?"}
Resume --> |Yes| Load["Load checkpoint path"]
Resume --> |No| Dump["Dump YAML/pickle params"]
Load --> Dump
Dump --> Learn["Runner.learn(max_iterations)"]
Learn --> Close["Close env and app"]
Close --> End(["End"])
```

**Diagram sources**
- [train.py:119-213](file://scripts/reinforcement_learning/rsl_rl/train.py#L119-L213)
- [manager_based_rl_env.py:110-133](file://source/isaaclab/isaaclab/envs/manager_based_rl_env.py#L110-L133)

**Section sources**
- [train.py:119-213](file://scripts/reinforcement_learning/rsl_rl/train.py#L119-L213)
- [manager_based_rl_env.py:110-133](file://source/isaaclab/isaaclab/envs/manager_based_rl_env.py#L110-L133)

### Manager-Based Environment System
- Manager registration: comprehensive task ID registry supporting flat, rough, play modes plus 5 ablation variants.
- Modular MDP components: commands, observations, rewards, terminations, curriculum, and event managers.
- Ablation configurations: specialized environment configs for each ablation variant with tailored observation groups.
- Custom observation functions: privileged observations (mass, COM, friction, gain scales) and contact sensors.

```mermaid
sequenceDiagram
participant Registry as "Task Registry"
participant EnvCfg as "Environment Config"
participant Managers as "MDP Managers"
Registry->>EnvCfg : Load manager-based config
EnvCfg->>Managers : Initialize command manager
EnvCfg->>Managers : Initialize reward manager
EnvCfg->>Managers : Initialize termination manager
EnvCfg->>Managers : Initialize curriculum manager
Managers-->>EnvCfg : Configure ablation-specific settings
EnvCfg-->>Registry : Return configured environment
```

**Diagram sources**
- [go2_parkour/__init__.py:19-51](file://source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/go2_parkour/__init__.py#L19-L51)
- [manager_based_rl_env_cfg.py:70-80](file://source/isaaclab/isaaclab/envs/manager_based_rl_env_cfg.py#L70-L80)

**Section sources**
- [go2_parkour/__init__.py:19-51](file://source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/go2_parkour/__init__.py#L19-L51)
- [manager_based_rl_env_cfg.py:70-80](file://source/isaaclab/isaaclab/envs/manager_based_rl_env_cfg.py#L70-L80)
- [rough_env_cfg.py:448-462](file://source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/go2_parkour/rough_env_cfg.py#L448-L462)

### Experiment Management (Configuration, Checkpoints, Results)
- Experiment naming: timestamped directory with optional run name; printed for downstream parsing.
- Parameter persistence: env and agent configs saved as YAML and pickle.
- Checkpoint loading: resolves checkpoint path for resume or distillation.
- IO descriptor export: manager-based environments support exporting input/output descriptors for policy deployment.
- Video logging: optional video recording during training.

```mermaid
sequenceDiagram
participant Runner as "OnPolicyRunner"
participant FS as "Filesystem"
participant IO as "IO Descriptor Export"
participant TB as "TensorBoard"
Runner->>FS : Create log_dir with timestamp
Runner->>FS : Dump env.yaml, agent.yaml, env.pkl, agent.pkl
Runner->>IO : Export IO descriptors if enabled
Runner->>Runner : Optionally load checkpoint
Runner->>TB : Periodically write metrics
Runner-->>FS : Store checkpoints and artifacts
```

**Diagram sources**
- [train.py:145-206](file://scripts/reinforcement_learning/rsl_rl/train.py#L145-L206)
- [train.py:157-165](file://scripts/reinforcement_learning/rsl_rl/train.py#L157-L165)

**Section sources**
- [train.py:145-206](file://scripts/reinforcement_learning/rsl_rl/train.py#L145-L206)
- [train.py:157-165](file://scripts/reinforcement_learning/rsl_rl/train.py#L157-L165)

### Hyperparameter Optimization with Ray
- Tuner workflow: builds invocation commands from sweep configs, executes trials, and streams metrics from TensorBoard logs.
- Resource orchestration: discovers GPU node resources, packs workers, and supports heterogeneous clusters.
- Submission: distributes aggregate jobs across clusters defined in a cluster config file.

```mermaid
sequenceDiagram
participant User as "User"
participant Tuner as "tuner.py"
participant Util as "util.py"
participant Ray as "Ray Cluster"
participant Trainer as "RL Trainer"
User->>Tuner : Provide cfg_file and cfg_class
Tuner->>Util : Build invocation command from cfg
Tuner->>Ray : Launch trials with resource constraints
Ray->>Trainer : Execute training process
Trainer->>Util : Write TensorBoard logs
Util-->>Tuner : Latest scalar metrics
Tuner-->>User : Best config and results
```

**Diagram sources**
- [tuner.py:66-160](file://scripts/reinforcement_learning/ray/tuner.py#L66-L160)
- [util.py:55-96](file://scripts/reinforcement_learning/ray/util.py#L55-L96)
- [util.py:310-366](file://scripts/reinforcement_learning/ray/util.py#L310-L366)
- [submit_job.py:79-107](file://scripts/reinforcement_learning/ray/submit_job.py#L79-L107)

**Section sources**
- [tuner.py:206-292](file://scripts/reinforcement_learning/ray/tuner.py#L206-L292)
- [util.py:20-53](file://scripts/reinforcement_learning/ray/util.py#L20-L53)
- [util.py:310-366](file://scripts/reinforcement_learning/ray/util.py#L310-L366)
- [submit_job.py:79-107](file://scripts/reinforcement_learning/ray/submit_job.py#L79-L107)

### Curriculum Learning Implementation
- Computes curriculum terms per environment IDs, logs them under a dedicated namespace, and resets term states after logging.
- Supports iterable active terms for downstream reporting.

```mermaid
flowchart TD
Start(["Compute Curriculum"]) --> Resolve["Resolve env_ids"]
Resolve --> Iterate["Iterate managed terms"]
Iterate --> State["Compute term state"]
State --> Log["Log under 'Curriculum/<name>'"]
Log --> Reset["Reset term states"]
Reset --> End(["Return extras"])
```

**Diagram sources**
- [curriculum_manager.py:124-173](file://source/isaaclab/isaaclab/managers/curriculum_manager.py#L124-L173)

**Section sources**
- [curriculum_manager.py:100-203](file://source/isaaclab/isaaclab/managers/curriculum_manager.py#L100-L203)

### Distributed Training Infrastructure and Scalability
- Multi-GPU training: adjusts device and seeds per local rank; updates environment device accordingly.
- Benchmarking: mirrors distributed setup for performance comparisons across frameworks.
- Resource wrapping: discovers node resources, normalizes heterogeneous lists, and schedules jobs with explicit GPU/CPU/RAM allocations.

```mermaid
flowchart TD
Start(["Distributed Start"]) --> Detect["Detect GPU nodes and resources"]
Detect --> Normalize["Fill missing resource args"]
Normalize --> Schedule["Schedule jobs with resource constraints"]
Schedule --> Train["Execute training with adjusted device/seeds"]
Train --> Monitor["Monitor logs and metrics"]
Monitor --> End(["Done"])
```

**Diagram sources**
- [train.py:99-125](file://scripts/reinforcement_learning/rl_games/train.py#L99-L125)
- [benchmark_rlgames.py:155-179](file://scripts/benchmarks/benchmark_rlgames.py#L155-L179)
- [util.py:310-366](file://scripts/reinforcement_learning/ray/util.py#L310-L366)
- [wrap_resources.py:86-116](file://scripts/reinforcement_learning/ray/wrap_resources.py#L86-L116)

**Section sources**
- [train.py:99-125](file://scripts/reinforcement_learning/rl_games/train.py#L99-L125)
- [benchmark_rlgames.py:155-179](file://scripts/benchmarks/benchmark_rlgames.py#L155-L179)
- [util.py:420-461](file://scripts/reinforcement_learning/ray/util.py#L420-L461)
- [wrap_resources.py:86-116](file://scripts/reinforcement_learning/ray/wrap_resources.py#L86-L116)

### Validation and Testing with Baselines
- Random agent: samples uniform random actions in [-1, 1] for vectorized environments.
- Zero agent: applies zero actions deterministically.
- Both run in the Isaac Lab environment and can be used to establish baselines for ablation comparisons.

```mermaid
sequenceDiagram
participant User as "User"
participant Rand as "Random Agent"
participant Zero as "Zero Agent"
participant Env as "Isaac Environment"
User->>Rand : Run with task and num_envs
Rand->>Env : Sample actions uniformly in [-1,1]
Env-->>Rand : Step results
User->>Zero : Run with task and num_envs
Zero->>Env : Apply zero actions
Env-->>Zero : Step results
```

**Diagram sources**
- [random_agent.py:41-65](file://scripts/environments/random_agent.py#L41-L65)
- [zero_agent.py:41-65](file://scripts/environments/zero_agent.py#L41-L65)

**Section sources**
- [random_agent.py:41-65](file://scripts/environments/random_agent.py#L41-L65)
- [zero_agent.py:41-65](file://scripts/environments/zero_agent.py#L41-L65)

### Practical Training Configuration Examples (Ablations)
- Abl 1: Actor uses prop-only; Critic uses prop + private + raw scan.
- Abl 2.5: Actor uses prop + raw scan; Critic uses prop + private + raw scan.
- Abl 3.5 (best): Actor and Critic both use prop + scan encoding.
- Abl 4.0: Actor uses prop + scan encoding; Critic uses prop + private + raw scan.
- Abl 7.0: Actor uses prop + scan encoding; Critic uses prop + private encoding + scan encoding.

**Updated** Enhanced with manager-based training examples including Go2-Parkour-Rough-v0 and Go2-Parkour-Rough-Abl3_5-v0 task IDs for comprehensive training approaches.

Training commands and environment counts are documented in the repository's README for both direct and manager-based training approaches, including headless and non-headless runs.

**Section sources**
- [README.md:120-172](file://README.md#L120-L172)
- [README.md:141-148](file://README.md#L141-L148)

### Experiment Setup Workflows
- Single-run training: use the RSL-RL training script with task IDs and environment counts.
- Manager-based registration: comprehensive task ID registry supports 14 variants (flat, rough, play, 5 ablations).
- Distributed runs: enable the distributed flag to adjust device and seeds per rank.
- Hyperparameter tuning: define sweep configurations and run the Ray tuner; aggregate jobs can be submitted to clusters.

**Section sources**
- [train.py:135-144](file://scripts/reinforcement_learning/rsl_rl/train.py#L135-L144)
- [go2_parkour/__init__.py:19-51](file://source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/go2_parkour/__init__.py#L19-L51)
- [tuner.py:206-292](file://scripts/reinforcement_learning/ray/tuner.py#L206-L292)
- [submit_job.py:129-149](file://scripts/reinforcement_learning/ray/submit_job.py#L129-L149)

### Result Analysis Procedures
- Metrics: TensorBoard logs are parsed periodically by the tuner to report metrics.
- Best configurations: selection criteria depend on the chosen metric and mode (max/min).
- Baselines: compare ablation curves against random and zero agents to assess meaningful policy improvement.

**Section sources**
- [util.py:20-53](file://scripts/reinforcement_learning/ray/util.py#L20-L53)
- [tuner.py:233-282](file://scripts/reinforcement_learning/ray/tuner.py#L233-L282)

## Dependency Analysis
- Training scripts depend on the Isaac Lab AppLauncher and environment/task registration.
- Manager-based environments integrate with comprehensive MDP manager system.
- RSL-RL runner depends on environment wrappers and configuration objects.
- Ray tuning depends on resource discovery and job submission clients.
- Curriculum manager integrates with environment instances to compute and log difficulty metrics.

```mermaid
graph LR
T["RSL-RL train.py"] --> RL["RSL-RL Runner"]
T --> ENV["ManagerBasedRLEnv"]
MB["Manager-Based Tasks"] --> ENV
ENV --> CM["Command Manager"]
ENV --> RM["Reward Manager"]
ENV --> TM["Termination Manager"]
ENV --> CURM["Curriculum Manager"]
RT["Ray tuner.py"] --> UT["util.py"]
RT --> SUB["submit_job.py"]
UT --> TB["TensorBoard"]
```

**Diagram sources**
- [train.py:95-101](file://scripts/reinforcement_learning/rsl_rl/train.py#L95-L101)
- [manager_based_rl_env.py:110-133](file://source/isaaclab/isaaclab/envs/manager_based_rl_env.py#L110-L133)
- [go2_parkour/__init__.py:19-51](file://source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/go2_parkour/__init__.py#L19-L51)
- [tuner.py:66-160](file://scripts/reinforcement_learning/ray/tuner.py#L66-L160)
- [util.py:20-53](file://scripts/reinforcement_learning/ray/util.py#L20-L53)
- [submit_job.py:79-107](file://scripts/reinforcement_learning/ray/submit_job.py#L79-L107)
- [curriculum_manager.py:124-173](file://source/isaaclab/isaaclab/managers/curriculum_manager.py#L124-L173)

**Section sources**
- [train.py:95-101](file://scripts/reinforcement_learning/rsl_rl/train.py#L95-L101)
- [manager_based_rl_env.py:110-133](file://source/isaaclab/isaaclab/envs/manager_based_rl_env.py#L110-L133)
- [go2_parkour/__init__.py:19-51](file://source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/go2_parkour/__init__.py#L19-L51)
- [tuner.py:66-160](file://scripts/reinforcement_learning/ray/tuner.py#L66-L160)
- [util.py:20-53](file://scripts/reinforcement_learning/ray/util.py#L20-L53)
- [submit_job.py:79-107](file://scripts/reinforcement_learning/ray/submit_job.py#L79-L107)
- [curriculum_manager.py:124-173](file://source/isaaclab/isaaclab/managers/curriculum_manager.py#L124-L173)

## Performance Considerations
- Headless training reduces overhead for large-scale environments.
- Multi-GPU training requires adjusting seeds and devices per rank to maintain diversity.
- Manager-based environments support IO descriptor export for optimized policy deployment.
- Resource normalization ensures efficient packing of heterogeneous clusters.
- Benchmarking utilities mirror distributed setups to compare across frameworks.

## Troubleshooting Guide
- Version compatibility: RSL-RL distributed training requires a minimum version; install the correct version if mismatched.
- Log extraction errors: tuner raises a specific error when experiment logs cannot be extracted; verify training script prints the expected lines and check timeouts.
- Cluster submission: ensure cluster config file exists and Ray dashboard URLs are reachable; logs are fetched post-execution.
- Resource misalignment: when PyTorch and GPU detection disagree, reset CUDA_VISIBLE_DEVICES to align visibility.
- Manager-based registration: verify task IDs are properly registered in the manager-based task registry.

**Section sources**
- [train.py:70-83](file://scripts/reinforcement_learning/rsl_rl/train.py#L70-L83)
- [tuner.py:173-204](file://scripts/reinforcement_learning/ray/tuner.py#L173-L204)
- [util.py:109-112](file://scripts/reinforcement_learning/ray/util.py#L109-L112)
- [util.py:151-200](file://scripts/reinforcement_learning/ray/util.py#L151-L200)
- [submit_job.py:58-76](file://scripts/reinforcement_learning/ray/submit_job.py#L58-L76)

## Conclusion
The repository provides a comprehensive, modular training and experimentation framework supporting ablation studies across five Go2 parkour architectures using both direct and manager-based training approaches. The enhanced manager-based system offers improved modularity with configurable MDP components, comprehensive task registration, and flexible ablation configurations. It integrates framework-specific runners, distributed orchestration via Ray, curriculum learning, and robust experiment management with IO descriptor export capabilities. Baseline agents and benchmarking utilities enable rigorous validation and performance comparisons, while practical examples and configuration guidance streamline reproducible workflows at scale.

## Appendices

### Appendix A: Ablation Specifications and Training Commands
- Abl 1: Actor = prop_obs only; Critic = prop_obs + priv_obs + raw scan
- Abl 2.5: Actor = prop_obs + raw scan; Critic = prop_obs + priv_obs + raw scan
- Abl 3.5 (best): Actor = prop_obs + scan encoding; Critic = prop_obs + priv_obs + scan encoding
- Abl 4.0: Actor = prop_obs + scan encoding; Critic = prop_obs + priv_obs + raw scan
- Abl 7.0: Actor = prop_obs + scan encoding; Critic = prop_obs + priv_obs encoding + scan encoding

**Updated** Enhanced with manager-based training examples:
- Direct approach: Go2-Rough-Direct-Abl3_5-v0 for traditional environment configuration
- Manager-based approach: Go2-Parkour-Rough-v0 for standard manager-based training, Go2-Parkour-Rough-Abl3_5-v0 for ablated manager-based training

Training commands and environment counts are provided in the repository's README for both direct and manager-based approaches.

**Section sources**
- [README.md:120-172](file://README.md#L120-L172)
- [README.md:141-148](file://README.md#L141-L148)

### Appendix B: Manager-Based Task Registration
- Flat terrain: Go2-Parkour-Flat-v0
- Rough terrain: Go2-Parkour-Rough-v0
- Play mode: Go2-Parkour-Rough-Play-v0
- Ablation variants: Go2-Parkour-Rough-Abl1-v0, Go2-Parkour-Rough-Abl2_5-v0, Go2-Parkour-Rough-Abl3_5-v0, Go2-Parkour-Rough-Abl4_0-v0, Go2-Parkour-Rough-Abl7_0-v0
- Play variants: Go2-Parkour-Rough-Abl1-Play-v0, Go2-Parkour-Rough-Abl2_5-Play-v0, Go2-Parkour-Rough-Abl3_5-Play-v0, Go2-Parkour-Rough-Abl4_0-Play-v0, Go2-Parkour-Rough-Abl7_0-Play-v0

**Section sources**
- [go2_parkour/__init__.py:19-161](file://source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/go2_parkour/__init__.py#L19-L161)

### Appendix C: Manager-Based Environment Configuration
- Manager-based RL environment configuration extends ManagerBasedRLEnvCfg with reward, termination, curriculum, and command settings.
- Ablation-specific configurations redefine observation groups for scan-first ordering and privileged observation encoders.
- Custom observation functions provide privileged observations (mass, COM, friction coefficients, gain scales) and contact sensor data.

**Section sources**
- [manager_based_rl_env_cfg.py:14-81](file://source/isaaclab/isaaclab/envs/manager_based_rl_env_cfg.py#L14-L81)
- [rough_env_cfg.py:572-757](file://source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/go2_parkour/rough_env_cfg.py#L572-L757)
- [observations.py:33-111](file://source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/go2_parkour/mdp/observations.py#L33-L111)

### Appendix D: Hyperparameter Sweep Example
- Example sweep configuration demonstrates varying environment counts and horizon lengths, selecting compatible mini-batch sizes derived from total batch constraints.

**Section sources**
- [vision_cfg.py:34-59](file://scripts/reinforcement_learning/ray/hyperparameter_tuning/vision_cfg.py#L34-L59)