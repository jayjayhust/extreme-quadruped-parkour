### main branch is direct method that implement go2, joint code 
### 3d branch is direct method that implement go2, 3d foot coordinate based code

You have to see /home/*/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/direct/go2 <--- implement

moreover, you can get some information about scripts/rein~/rsl_rl/train.py

- 2025.09.17 : Forward, Inverse Kinematics clear, simplify and make up go2_env clearly and implement class for Dynamics solver  
- 2025.09.19 : Inverse Kinemtaics divergence solve, add rew_default_close in branch "3d_IK_no_divergence"


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
