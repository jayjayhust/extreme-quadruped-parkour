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

#### Training unitree GO2
##### 기본 학습: reset idx 안 바꾸면, 매 episode마다 다른 속도 명령을 줘서 학습 -> 전진, 후진, 좌우, 회전 등 모든 움직임 학습
> 기본 학습 명령어(만마리 학습)
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task=Go2-Direct-v0 --headless --num_envs 10000
```
> Rough Terrain 학습 명령어
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Go2-Rough-Direct-v0 --headless --num_envs 10000
```

##### 고정 Command를 줘서 학습하는법
```python
# go2_env.py의 _reset_idx 메서드 수정
def _reset_idx(self, env_ids: torch.Tensor | None):
    # ... 기존 코드 ...
    
    # 고정 명령 설정
    fixed_command = torch.tensor([1.0, 0.0, 0.0], device=self.device)  # [x_vel, y_vel, yaw_rate]
    self._commands[env_ids] = fixed_command.expand(len(env_ids), 3)
```
##### Tensorboard로 학습 확인
```bash
tensorboard --logdir logs/rsl_rl/go2_flat_direct
```
OR
```bash
tensorboard --logdir logs/rsl_rl/go2_flat_direct/2025-09-26_22-02-15/ --host 0.0.0.0 --port 6006
```
> 참고: Tensorboard에 필요한 모든 데이터 정보는 아래 경로에 있음(이 파일 가지고 그래프를 그리는것임).
logs/rsl_rl/go2_flat_direct/2025-09-26_22-02-15/events.out.tfevents.1758891741.yobel-desktop.453323.0

#### Playing unitree GO2
> 참고: 내가 주고 싶은 command로 가게 하고 싶으면, reset idx에서 학습에 적어놓은거처럼, command fix하기
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task=Go2-Direct-v0 --num_envs 10
```
##### Playing unitree GO2: 특정 model.pt 파일 돌리고 싶을 때
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task=Go2-Direct-v0 --checkpoint logs/rsl_rl/go2_flat_direct/2025-09-26_15-00-56/model_4999.pt
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
