### main branch is direct method that implement go2, joint code 
### 3d branch is direct method that implement go2, 3d foot coordinate based code
- 2025.09.17(대걸님) : Forward, Inverse Kinematics clear, simplify and make up go2_env clearly and implement class for Dynamics solver  
- 2025.09.19(대걸님) : Inverse Kinemtaics divergence solve, add rew_default_close in branch "3d_IK_no_divergence"
You have to see "/home/*/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/direct/go2" <--- implement
moreover, you can get some information about scripts/rein~/rsl_rl/train.py

#### Key Folders_Yobel
##### PPO setting(configuration) is at here
source/isaaclab_tasks/isaaclab_tasks/direct/go2/agents/rsl_rl_ppo_cfg.py
##### rsl_rl learning package: RL Algorithms are at here
- rsl_rl/runners/on_policy_runner.py → OnPolicyRunner
- rsl_rl/algorithms/ppo.py → PPO 업데이트 로직
- rsl_rl/modules/actor_critic.py → Actor–Critic 네트워크/분포
- rsl_rl/storage/rollout_storage.py → Rollout 버퍼/GAE
##### Task name is written at here
"isaaclab_tasks/direct/go2/init.py"

#### When you first cloned
##### IsaacSim 5.0
```bash
conda activate env_isaaclab5
./isaaclab.sh -i
```
##### IsaacSim 4.5
```bash
conda activate env_isaaclab
./isaaclab.sh -i
```
##### If Error happens use below
```bash
conda activate env_isaaclab && cd source/isaaclab_tasks && pip install -e .
```
```bash
cd /home/yobellee/Desktop/LAIR/Isaaclab_direct_go2
pip install -e source/isaaclab_tasks
```

#### Training unitree GO2_direct_ours
##### 기본 학습: reset idx 안 바꾸면, 매 episode마다 다른 속도 명령을 줘서 학습 -> 전진, 후진, 좌우, 회전 등 모든 움직임 학습
> Flat Terrain 기본 학습 명령어(예: 만마리 학습): Random Command
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task=Go2-Direct-v0 --headless --num_envs 10000
```
> Flat Terrain에서 fixed command로 학습
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Go2-Direct-v0 --headless --num_envs 2048 env.command_mode=fixed env.fixed_command='[1.0,0.0,0.0]'
```
> **Rough Terrain 기본 학습 명령어(예: 2048마리 학습): Random Command** : Random Command 숫자는 go2_env.py에서 바꿔야 함.
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Go2-Rough-Direct-v0 --headless --num_envs 2048
```
> **Rough Terrain 변형: fixed command로 학습 (커리큘럼 유지, 단 고정 명령)**
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Go2-Rough-Direct-v0 --headless --num_envs 2048 env.command_mode=fixed env.fixed_command='[0.5,0.0,0.0]'
```
>**Rought Terrain 변형: 커리큘럼 끄고, random command, resetidx에서 random하게 spawn되도록 코드 수정_25_10_21**
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task=Go2-Rough-Direct-v0 --headless --num_envs 2048 env.use_curriculum=False
```
>**Rought Terrain 변형: 체크포인트 이후 연속해서 학습, 커리큘럼 끄고, random command, resetidx에서 random하게 spawn되도록 코드 수정_25_10_21**
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Go2-Rough-Direct-v0 --headless --num_envs 2048 --resume --load_run 2025-10-21_21-46-39 --checkpoint model_19999.pt --max_iterations 10000 env.use_curriculum=False
```
> **Rough Terrain heading alignment(default=ON): yaw 명령이 목표 heading을 추종하도록 활성화_25_12_20**  
> 끄고 싶으면 `env.heading_command=False`로 덮어써 주세요.
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Go2-Rough-Direct-v0 --headless --num_envs 4096
```

#### Playing unitree GO2_direct_ours
##### Flat Terrain Playing
> 고정 커맨드로 Play
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task=Go2-Direct-v0 --num_envs 10 env.command_mode=fixed
```
> 특정 model.pt 파일 돌리고 싶을 때
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task=Go2-Direct-v0 env.command_mode=fixed --checkpoint logs/rsl_rl/go2_flat_direct/2025-09-26_15-00-56/model_4999.pt
```
> 랜덤 커맨드로 플레이
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task=Go2-Direct-v0 --num_envs 10
```

###### Rough Terrain Playing
> 기본 명령어: **fixed command** + curriculum off, 다른 무작위 지형
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task Go2-Rough-Direct-Play-v0 --num_envs 10
```
> **fixed command** - 특정 model.pt 파일 돌리고 싶을 때 + 48초 길이의 비디오 녹화
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task Go2-Rough-Direct-Play-v0 --num_envs 10 --checkpoint logs/rsl_rl/go2_flat_direct/2025-09-26_15-00-56/model_4999.pt --video --video_length 2400
```
> 변형: random command로 테스트
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task Go2-Rough-Direct-Play-v0 --num_envs 10 env.command_mode=random
```
> 변형: **fixed command**, 커리큘럼 끄고 무작위 환경에서 Play
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task=Go2-Rough-Direct-Play-v0 --num_envs=10 env.use_curriculum=False
```
> 변형: **fixed command**, heading도 키고 커리큘럼 킴: 학습에서 사용했던 승급/강등 환경 그대로_25_10_24
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task Go2-Rough-Direct-v0 --num_envs 50 env.command_mode=fixed env.fixed_command='[0.5,0.0,0.0]' env.heading_command=True env.command_heading_range='[0.0,0.0]' env.heading_control_stiffness=3.0 env.command_yaw_range='[-0.15,0.15]' env.command_log_interval=50 env.command_log_env=0 env.rel_heading_envs=1.0 env.rel_standing_envs=0.0
```
> 변형: **fixed command**, heading 끄고, 커리큘럼 킴: 학습에서 사용했던 승급/강등 환경 그대로_25_10_24
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task Go2-Rough-Direct-v0 --num_envs 50 env.command_mode=fixed env.fixed_command='[1.0,0.0,0.0]' env.heading_command=False env.command_log_interval=50 env.command_log_env=0
```

#### Tensorboard로 학습 확인
##### Flat Terrain
```bash
tensorboard --logdir logs/rsl_rl/go2_flat_direct
```
OR
```bash
tensorboard --logdir logs/rsl_rl/go2_flat_direct/2025-09-26_22-02-15/ --host 0.0.0.0 --port 6006
```
> 참고: Tensorboard에 필요한 모든 데이터 정보는 아래 경로에 있음(이 파일 가지고 그래프를 그리는것임).
logs/rsl_rl/go2_flat_direct/2025-09-26_22-02-15/events.out.tfevents.1758891741.yobel-desktop.453323.0
##### Rough Terrain
```bash
tensorboard --logdir logs/rsl_rl/go2_rough_direct
```
OR
```bash
tensorboard --logdir logs/rsl_rl/go2_rough_direct/2025-09-26_22-02-15/ --host 0.0.0.0 --port 6006
```

#### Training & Playing unitree GO2_managerbased_from_IsaacLab
> Training
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Velocity-Rough-Unitree-Go2-v0 --headless --num_envs 2048
```
> Playing in same training curriculum (curriculum ON)
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task Isaac-Velocity-Rough-Unitree-Go2-v0 --num_envs 50
```
> Yaw제어허용
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
--task Isaac-Velocity-Rough-Unitree-Go2-v0 --num_envs 100 \
env.commands.base_velocity.ranges.lin_vel_x=[0.5,0.5] \
env.commands.base_velocity.ranges.lin_vel_y=[0.0,0.0] \
env.commands.base_velocity.ranges.ang_vel_z=[-0.5,0.5] \
env.commands.base_velocity.ranges.heading=[0.0,0.0] \
env.commands.base_velocity.heading_control_stiffness=2.0 \
env.commands.base_velocity.rel_heading_envs=1.0 \
env.commands.base_velocity.rel_standing_envs=0.0 \
env.commands.base_velocity.resampling_time_range=[9999,9999]
```
> 초기 yaw 0 고정
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
--task Isaac-Velocity-Rough-Unitree-Go2-v0 --num_envs 100 \
env.commands.base_velocity.ranges.lin_vel_x=[1.0,1.0] \
env.commands.base_velocity.ranges.lin_vel_y=[0.0,0.0] \
env.commands.base_velocity.ranges.ang_vel_z=[0.0,0.0] \
env.commands.base_velocity.ranges.heading=[0.0,0.0] \
env.commands.base_velocity.rel_standing_envs=0.0 \
env.commands.base_velocity.resampling_time_range=[9999,9999] \
env.events.reset_base.params.pose_range.yaw=[0.0,0.0]
```
> Playing in non training curriculum (curriculum OFF)
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task Isaac-Velocity-Rough-Unitree-Go2-Play-v0 --num_envs 50 
```


#### Infos
“std + action scale + clipping”이 합쳐져서
→ 결국 에이전트가 학습 초기에 탐색할 수 있는 action 영역이 결정

## License

The Isaac Lab framework is released under [BSD-3 License](LICENSE). The `isaaclab_mimic` extension and its corresponding standalone scripts are released under [Apache 2.0](LICENSE-mimic). The license files of its dependencies and assets are present in the [`docs/licenses`](docs/licenses) directory.

## Acknowledgement

Isaac Lab development initiated from the [Orbit](https://isaac-orbit.github.io/) framework. We would appreciate if you would cite it in academic publications as well:

```
@article{mittal2023orbit,
   author={Mittal, Mayank and Yu, Calvin and Yu, Qinxi and Liu, Jingzhou and Rudin, Nikita and Hoeller, David and Yuan, Jia Lin and Singh, Ritvik and Guo, Yunrong and Mazhar, Hammad and Mandlekar, Ajay and Babich, Buck and State, Gavriel and Hutter, Marco and Garg, Animesh},
   journal={IEEE Robotics and Automation Letters},
   title={Orbit: A Unified Simulation Framework for Interactive Robot Learning Environments},
   year={2023},
   volume={8},
   number={6},
   pages={3740-3747},
   doi={10.1109/LRA.2023.3270034}
}
