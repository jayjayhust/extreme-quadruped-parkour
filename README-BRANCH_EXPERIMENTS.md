# README-BRANCH_EXPERIMENTS_v04

This file documents experiment explanation and what each branch was intended to test.
Content is summarized from the Lab Meeting PPT decks (01-04) and the research notes from GOODNOTE.

Sources used
- 01. LabMeeting-Ablation Study(Flat Terrain)_v04_25_10_13.pptx
- 02. LabMeeting-Rough Terrain Study_v05_25_10_17.pptx
- 03. LabMeeting-Rough Terrain Study_v04_25_10_24.pptx
- 04. LabMeeting-Network Ablation Study for Stable Locomotion on Rough Terrain_v01_260101.pptx
- Research notes PDFs in Research_Full_Process_GoodNotes
  - Ablation Study, Rough Terrain Study, Encoding Latent Ablation Study

**Naming and ablation keys**
- Flat ablation cases (LabMeeting 01):
  - Case 1: observation = base obs (root lin/ang vel, projected gravity, commands) + last_action (3D foot action space); no joint_pos/vel.
  - Case 2: base obs + joint_pos + joint_vel; no last_action.
  - Case 3: base obs + joint_pos + joint_vel + last_action (3D foot action space) (baseline).
- Network ablation keys (LabMeeting 04, Parkour Step focus):
  - Abl 1: Actor input = prop_obs only (blind walking)
    - Actor input: prop_obs(52D)
    - Critic input: priv_scan(187D), priv_obs(29D), prop_obs(52D)
  - Abl 2.5: Actor input = raw scandot (priv_scan)
    - Actor input: priv_scan(187D), prop_obs(52D)
    - Critic input: priv_scan(187D), priv_obs(29D), prop_obs(52D)
  - Abl 3.5: Actor + Critic input = scandotEncoding (z_scan)
    - Actor input: priv_scan(187D)->MLP->z_scan(32D), prop_obs(52D)   
    - Critic input: priv_scan(187D)->MLP->z_scan(32D), priv_obs(29D), prop_obs(52D)
  - Abl 4.0: Actor = scandotEncoding, Critic = raw scandot
    - Actor input: priv_scan(187D)->MLP->z_scan(32D), prop_obs(52D)   
    - Critic input: priv_scan(187D), priv_obs(29D), prop_obs(52D)  
  - Abl 7.0: Abl 3.5 + Critic priv_obsEncoding
    - Actor input: priv_scan(187D)->MLP->z_scan(32D), prop_obs(52D)   
    - Critic input: priv_scan(187D)->MLP->z_scan(32D), priv_obs(29D)->MLP->z_priv_obs(20D), prop_obs(52D)      
- Terrain labels used below:
  - Flat: flat terrain experiments
  - Rough: rough terrain curriculum experiments
  - HardTerrain: harder rough terrain with gaps/parkour emphasis
  - ParkStep: parkour step / gap focused terrain set

-------------------------------------------------------------------------------

## Flat terrain - 3D action-space observation ablation (LabMeeting 01)
Purpose
- Hypothesis: mixing joint-space (joint_pos/vel) and 3D-space (last_action) in one
  observation causes mismatch; test which observation set is best.
Common settings
- Training: 4096 envs, 10000 iterations.
- Success criteria: vx_cmd = 3.0 and vx_cmd = 3.0 with yaw_vel = 2.0.
Results summary (LabMeeting 01)
- Case 1: fails at vx_cmd = 3.0 (max); passes up to vx_cmd = 2.5 and vx_cmd = 2.0 with yaw=2.0.
- Case 2: succeeds at vx_cmd = 3.0 and vx_cmd = 3.0 with yaw=2.0. Best among 3 Cases.
- Case 3: succeeds at vx_cmd = 3.0 but fails at vx_cmd = 3.0 with yaw=2.0 ; passes up to vx_cmd = 3.0 and vx_cmd = 2.5 with yaw=2.0.

Branches
- 3d-ablation_for_mismatch_actionspaces_v02_250926
  - Early flat ablation baseline (pre v04).
- 3d-ablation_for_mismatch_actionspaces_v03_250926
  - Early flat ablation baseline (pre v04).
- 3d-ablation_for_mismatch_actionspaces_v04_250926
  - Flat ablation baseline for Case comparisons.
- 3d-ablation_for_mismatch_actionspaces_v04-only_last_action_250926
  - Case 1 (base obs + last_action; no joint_pos/vel). Fails at vx_cmd=3.0.
- 3d-ablation_for_mismatch_actionspaces_v04-only_jointposvel_250926
  - Case 2 (base obs + joint_pos + joint_vel; no last_action). Best among 3 Cases.
- 3d-ablation_for_mismatch_actionspaces_v04-only_jointposvel_lastaction_250926
  - Case 3 (base obs + joint_pos + joint_vel + last_action). Fails at vx_cmd=3.0 with yaw=2.0. Success at vx_cmd = 3.0 and vx_cmd = 2.5 with yaw=2.0.

**Velocity debugging**
- Goal: compare commanded vs actual root velocity for Case 2 and Case 3.
- Case 3 fails at vx=3.0, yaw=2.0, so debugging was conducted using vx=2.5, yaw=2.0.

Branches
- 3d-ablation_for_mismatch_actionspaces_showing_root_vel_v05-only_last_action_251001
  - Root-velocity debugging for Case 1.
- 3d-ablation_for_mismatch_actionspaces_showing_root_vel_v05-only_jointposvel_251001
  - Root-velocity debugging for Case 2.
- 3d-ablation_for_mismatch_actionspaces_showing_root_vel_v05-only_jointposvel_lastaction_251001
  - Root-velocity debugging for Case 3.

**Reward-scale sweep (Test1-5)**
- Goal: compare Case 2 vs Case 3 with 5 reward-scale variants. -> Changing reward-scales.
- Training: 10000 envs, 10000 iterations (LabMeeting 01).
- Notes: Test 1/3/5 look best; Test 5 seems best overall.
Branches (Case 2)
- 3d-ablation_for_mismatch_actionspaces-varying_reward_scale_v06-only_jointposvel_251002
- 3d-ablation_for_mismatch_actionspaces-varying_reward_scale_test1_v06-only_jointposvel_251002
- 3d-ablation_for_mismatch_actionspaces-varying_reward_scale_test2_v06-only_jointposvel_251002
- 3d-ablation_for_mismatch_actionspaces-varying_reward_scale_test3_v06-only_jointposvel_251002
- 3d-ablation_for_mismatch_actionspaces-varying_reward_scale_test4_v06-only_jointposvel_251002
- 3d-ablation_for_mismatch_actionspaces-varying_reward_scale_test5_v06-only_jointposvel_251002
Branches (Case 3)
- 3d-ablation_for_mismatch_actionspaces-varying_reward_scale_v06-only_jointposvel_lastaction_251002
- 3d-ablation_for_mismatch_actionspaces-varying_reward_scale_test1_v06-only_jointposvel_lastaction_251002
- 3d-ablation_for_mismatch_actionspaces-varying_reward_scale_test2_v06-only_jointposvel_lastaction_251002
- 3d-ablation_for_mismatch_actionspaces-varying_reward_scale_test3_v06-only_jointposvel_lastaction_251002
- 3d-ablation_for_mismatch_actionspaces-varying_reward_scale_test4_v06-only_jointposvel_lastaction_251002
- 3d-ablation_for_mismatch_actionspaces-varying_reward_scale_test5_v06-only_jointposvel_lastaction_251002

**Yaw oscillation follow-ups (Test5)**
- Goal: isolate yaw oscillation; test single env and yaw-only or lin+yaw.
- Observation: yaw tracks well at low lin_vel; oscillation likely from aggressive turning with high lin_vel.
Branches
- 3d-ablation_for_mismatch_actionspaces-varying_reward_scale_test5_v06.5_testing_lin_yaw-only_jointposvel_lastaction_251002
- 3d-ablation_for_mismatch_actionspaces-varying_reward_scale_test5_v06.5_testing_only_yaw-only_jointposvel_lastaction_251002

-------------------------------------------------------------------------------

## Rough terrain - joint-space scandot and curriculum (LabMeeting 02/03)
Purpose
- Extend flat results to rough terrain; build and tune curriculum logic.
- Recap from LabMeeting 01: Case 3 obs and reward scale Test5 were best on flat.
Curriculum notes (LabMeeting 02)
- Move up if distance > 4m (half of 8m sub-terrain length).
- Move down if distance < 0.5 * expected distance from command velocity.

**Exp 1 baseline**
- Joint space + scandot, 2048 envs, 3000 iterations.
- Result: fails to step; curriculum not working (needs fix).
Branch
- Joint_rough_terrain_scandot-o_v01_25_10_13
  - Baseline rough joint-space + scandot; failure due to curriculum issues.

**Curriculum integrated**
- Add curriculum and adjust reward scales for rough terrain.
- max_init_terrain_level = 1 (spawn from level 0-1).
Branch
- Joint_rough_terrain_scandot-o_v02-Curriculum_25_10_13
  - Curriculum enabled, 2048 envs, 3000 iterations.

**Base-height relative (curriculum)**
- Change base_height reward to be relative to ground height; adjust scales.
- Test1/Test2 reward-scale variants; later run 10000 iterations.
- Observation: stair "flop" behavior improved.
Branch
- Joint_rough_terrain_scandot-o_v03-Curriculum_baseheight_rel_25_10_15
  - Base height relative + reward-scale tests.
- Joint_rough_terrain_scandot-o_v03-Curriculum_baseheight_rel-Train_Play_Switch_Easier_25_10_17
  - Train/play switch to ease evaluation.

**Curriculum coefficient tuning (from research notes)**
- Goal: tune move_up/move_down thresholds to stabilize curriculum.
Branches
- Joint_rough_terrain_scandot-o_v04-Curriculum_movedown_coeff_lower_25_10_18
  - Lower move_down coefficient.
- Joint_rough_terrain_scandot-o_v05-Curriculum_moveup_coeff_lower_25_10_19
  - Lower move_up coefficient.
- Joint_rough_terrain_scandot-o_v06-Curriculum_moveupdown_coeff-both-lower_25_10_21
  - Lower both move_up and move_down.

**Curriculum off and manager-based alignment (from research notes)**
Branches
- Joint_rough_terrain_scandot-o_v07-NoCurriculum_randomreset_25_10_21
  - Random reset path added for curriculum-off runs (requires `use_curriculum=False`; config here still True).
- Joint_rough_terrain_scandot-o_v08-ManagerBased_Running_25_10_22
  - Manager-based reference run for comparison.
- Joint_rough_terrain_scandot-o_v09-Curriculm_with_managerbased-scence-setting_25_10_23
  - Direct env aligned with manager-based scene settings.
- Joint_rough_terrain_scandot-o_v10-Curriculum_with_managerbased-headingcommand_25_10_23
  - Heading command added (manager-based style).
- Joint_rough_terrain_scandot-o_v11-headingcommand_Probsolving_25_10_24
  - Heading command troubleshooting resolved
  - **Best** Rough Terrain Locomotion in joint space.

Other joint-space baselines
- Joint_rough_terrain_v01_25_10_13
  - Rough joint-space baseline (Draft version).
- Joint_v01_25_10_13
  - Joint-space baseline (Draft version).

-------------------------------------------------------------------------------

## Rough terrain - 3D scandot series (from research notes)
Purpose
- Improve 3D action-space rough terrain by action squashing, scaling, and
  dexterous workspace sampling to handle stairs/gaps.
Branches
- 3d-rough_terrain_scandot-o_v01-reference_code_from_Joint_rough_251024
  - 3D rough baseline derived from joint rough reference(Joint_rough_terrain_scandot-o_v11-headingcommand_Probsolving_25_10_24).
- 3d-rough_terrain_scandot-o_v02-scaleup_to_overcome_stair-height_251025
  - Increase action scale to overcome stair height.
- 3d-rough_terrain_scandot-o_v03-tanh_on_action_to_overcome_stair-height_251027
  - Apply tanh to action outputs(mean, noise_std). -> rollout's distribution and update's distribution mismatch
- 3d-rough_terrain_scandot-o_v04-tanh_on_only_mean_to_overcome_stair-height_251027
  - Apply tanh to action mean only. -> solved mismatching issue between rollout and update distribution
- 3d-rough_terrain_scandot-o_v05-tanh_on_only_mean_action-scaling_251028
  - Mean-only tanh + action scaling considering feet's dexterous workspace -> Adjusting the scale to match the upper bound of the dexterous workspace..
- 3d-rough_terrain_scandot-o_v06-tanh_on_only_mean_action-dexterous_workspace_sampling_251028
  - Accounting for the asymmetric dexterous workspace by applying axis-specific center offsets.
- 3d-rough_terrain_scandot-o_v07-tanh_on_only_mean_action-dexterous_workspace_action0-same-default_251028
  - Force action=0(zero-action) to default in workspace sampling. -> our action is the residual of the default pos, so when the action is 0, it has to be the default pos. But the prev branch didn't sustain this -> experiment the different dexterous workspace ranges(50%, 40%, 30%)
- 3d-rough_terrain_scandot-o_v08-tanh_on_only_mean_action-dexterous_workspace-50%_action0-same-default_251029
  - Using only 50% of the full dexterous workspace range. -> After that experimented by varying the range per axis, rather than scaling the entire dexterous workspace uniformly.
- 3d-rough_terrain_scandot-o_v09-reference_branch-3d-rough_terrain_scandot-o_v01_25_11_03
  - 3d ref branch
  - Changed "3d-rough_terrain_scandot-o_v01-reference_code_from_Joint_rough_251024" to not consider dexterous workspace -> changing scales slightly(IK sclae has been changed too. IK penalty to -0.1)
- 3d-rough_terrain_scandot-o_v09-1-IKnotchanging-reference_branch-3d-rough_terrain_scandot-o_v01_25_11_04
  - IK back to its scale=-10.0 test.
- 3d-rough_terrain_scandot-o_v10-zvelreward-0-reference_branch-3d-rough_terrain_scandot-o_v01_25_11_04
  - changed "3d-rough_terrain_scandot-o_v09-reference_branch-3d-rough_terrain_scandot-o_v01_25_11_03"'s z-velocity reward scale to 0.
  - **Best** Rough Terrain Locomotion in 3d space @ 20000 iter training.
- 3d-rough_terrain_scandot-o_v11-changingscales-reference_branch-3d-rough_terrain_scandot-o_v01_25_11_04
  - Reward-scale adjustments from 3d ref branch.
- 3d-rough_terrain_scandot-o_v12-tanh_on_only_mean_action-dexterous_workspace-zvel0_251108
  - z-vel reward 0 with dex workspace.
- 3d-rough_terrain_scandot-o_v13-tanh_on_only_mean_action-dexterous_workspace-zvel-0.2_251109
  - z-vel reward -0.2 with dex workspace.
- 3d-rough_terrain_scandot-o_v14-tanh_on_only_mean_action-dexterous_workspace-diff-combinations_251110
  - Different dex workspace combinations.

-------------------------------------------------------------------------------

## Encoding Latent (Network Ablation) - base rough ablations (Rough)
Purpose
- Compare actor/critic input composition and scan encoding (RMA-inspired, ExtemeParkour-inspired).
- Research notes ranking: Ablation 2 < Ablation 2.5 < Ablation 4 < Ablation 3.
Branches
- EncodingLatent_Ablation1-Go2_our_base_v01_25_11_24
  - Baseline (our base) rough setup.
- EncodingLatent_Ablation1-Go2_our_base_v02-asymmetric_actorcriticobs_25_11_25
  - Asymmetric actor/critic observations.
- EncodingLatent_Ablation1-Go2_our_base_v03-mass_randomization_25_11_25
  - Mass randomization enabled.
- EncodingLatent_Ablation1-Go2_our_base_v04-mass_randomization_editting_25_11_26
  - Mass randomization edits.
- EncodingLatent_Ablation2-prop_obs-MLP_v01_25_11_25
- EncodingLatent_Ablation2-prop_obs-MLP_v02_25_11_26
  - Prop obs encoding via MLP.
- EncodingLatent_Ablation2.5_Input-ActorCritic_Privscan_v01_25_11_28
  - Actor and critic input raw priv scan.
- EncodingLatent_Ablation3-ScandotEncoding_to_Actor_Critic_v01_25_11_27
  - Encoded scan to actor and critic (best in rough ablation notes).
- EncodingLatent_Ablation4_Input-Actor_ScandotEncoding-Critic_RawScandot_v01_25_11_27
  - Actor encoded scan; critic raw scan (worse than Abl3).

-------------------------------------------------------------------------------

## Encoding Latent (Network Ablation) - HardTerrain (HardTerrain)
Purpose
- Harder terrain (gap/parkour emphasis, but no parkour step). **Abl3 generally best** but z-vel reward caused instability in some runs; later zvel_scale=0 series used.
Branches
- EncodingLatent_HardTerrain_Abl1-Go2_our_base_v01_25_11_30
  - HardTerrain baseline.
- EncodingLatent_HardTerrain_Abl1-Go2_our_base_v01-diffRewardScale_25_11_30
  - Reward-scale variant.
- EncodingLatent_HardTerrain_Abl1-Go2_our_base_v02-terrain_row_10_zveldown_25_12_02
  - Increase terrain difficulty (row 10) + reduce z-vel reward.
- EncodingLatent_HardTerrain_Abl2.5-ActorCritic_Privscan_v01_25_12_03
  - Actor/critic priv scan.
- EncodingLatent_HardTerrain_Abl3-ScandotEncoding_to_Actor_Critic_v01_25_12_02
  - Encoded scan to actor and critic; **best** in notes but z-vel reward unstable.
- EncodingLatent_HardTerrain_Abl4-Actor_ScandotEncoding-Critic_PrivScan_v01_25_12_03
  - Actor encoded scan; critic priv scan.
- EncodingLatent_HardTerrainExceptGap_Abl1-Go2_our_base_v01_251203
  - HardTerrain without gap.

-------------------------------------------------------------------------------

## Encoding Latent (Network Ablation) - HardTerrain zvel0 series (HardTerrain)
Purpose
- Remove z-velocity reward(z_vel_reward_scale=0) to reduce instability; explore scan/priv encodings.
Notes from research PDFs
- Abl3 (scan encoding to actor+critic(sharednetwork_which-is-wrong)) generally better than Abl1(propobs only to actor).
- Abl7.0(Abl3.5 + priv_obsEncoding to critic) reported better than Abl8.0(Abl3.5 + "priv_obs&priv_scan"Encoding to critic) and Abl3.5(scan encoding to actor+critic(sharednetworkX)); However, in sim_videos Abl3.5 seems better.
Branches
- EncodingLatent_HardTerrain_zvel0_Abl1-Actor_popobs_v01_25_12_04
  - Actor prop obs only.
- EncodingLatent_HardTerrain_zvel0_Abl2.5-ActorCritic_Privscan_v01_25_12_04
  - Actor/critic raw priv scan.
- EncodingLatent_HardTerrain_zvel0_Abl3-ScandotEncoding_to_Actor_Critic_v01-zvel0_25_12_04
  - Encoded scan to actor + critic.
- EncodingLatent_HardTerrain_zvel0_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v01-zvel0_25_12_09
  - Separate scan encoders for actor and critic.
  - **Best** result in simulation video
- EncodingLatent_HardTerrain_zvel0_Abl4-Actor_ScandotEncoding-Critic_PrivScan_v01_25_12_05
  - Actor encoded scan; critic priv scan.
- EncodingLatent_HardTerrain_zvel0_Abl5-Abl3+pobsEncoding_to_Actor_v01-zvel0_25_12_08
  - Abl3 + prop-obs encoding to actor.
- EncodingLatent_HardTerrain_zvel0_Abl5.5-Abl3.5+pobsEncoding_to_Actor_v01-zvel0_25_12_09
  - Abl3.5 + prop-obs encoding to actor.
- EncodingLatent_HardTerrain_zvel0_Abl6-Abl3+pobsEncoding_to_ActorCritic_v01-zvel0_25_12_08
  - Abl3 + prop-obs encoding to actor + critic.
- EncodingLatent_HardTerrain_zvel0_Abl6.5-Abl3.5+pobsEncoding_to_ActorCritic_v01-zvel0_25_12_09
  - Abl3.5 + prop-obs encoding to actor + critic.
- EncodingLatent_HardTerrain_zvel0_Abl7.0-Abl3.5+privobsEncoding_to_Critic_v01_25_12_10
  - Abl3.5 + priv-obs encoding to critic (Abl7 vs Abl8 comparison in notes).
  - **Best** result in graphs
- EncodingLatent_HardTerrain_zvel0_Abl8.0-Abl3.5+Critic-privobs_and_priv_scan_Encoding_to_Critic_v01_25_12_10
  - Abl3.5 + Critic encodes both priv obs and priv scan (Abl8; worse than Abl7 in notes).

-------------------------------------------------------------------------------

## Encoding Latent (Network Ablation) - collision/energy/wallclimb (ParkStep)
Purpose
- Add collision term and energy penalty reward for more parkour-like tasks; sweep reward scales.
Branches
- EncodingLatent_collide-energy-wallclimb_Abl1.0-Actor_popobs_v01_251215
  - Actor prop obs only.
- EncodingLatent_collide-energy-wallclimb_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v01_251213
  - Abl3.5 base in collide/energy setting.
**Reward-scale sweeps (Test11-15).**: Test10,12,13 GOOD  
- EncodingLatent_collide-energy-wallclimb_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v02-Test11rewardscale_251215
- EncodingLatent_collide-energy-wallclimb_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v03-Test12rewardscale_251216
- EncodingLatent_collide-energy-wallclimb_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v03-Test13rewardscale_251216
- EncodingLatent_collide-energy-wallclimb_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v03-Test13-2rewardscale_251218
- EncodingLatent_collide-energy-wallclimb_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v03-Test14rewardscale_251217
- EncodingLatent_collide-energy-wallclimb_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v03-Test15rewardscale_251218
  - Reward-scale sweeps (Test11-15); **Test10,12,13 GOOD**
- EncodingLatent_collide-energy-wallclimb_Abl7.0-Abl3.5+privobsEncoding_to_Critic_v01_251215
  - Add priv-obs encoding to critic.

-------------------------------------------------------------------------------

## Encoding Latent (Network Ablation) - ParkStep heading/workclamp (Extreme Parkour Rough Terrain)
Purpose (LabMeeting 04)
- Hard rough terrain with gaps and parkour steps. Heading command to keep straight (heading range 0 rad). Compare network's encoding choices with Rewardscale=Test25.
- **Best** in LabMeeting 04: Abl 3.5 (encoded scan to actor + critic).

Branches: Heading(+-1.6rad) + workclamp (Test20/21)
- EncodingLatent_col-E-ParkStep_Heading+workclamp_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v01-Test20Reward_251220
- EncodingLatent_col-E-ParkStep_Heading+workclamp_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v01-Test21Reward_251220

Branches: Heading shorter(+-0.2rad) + workclamp
- EncodingLatent_col-E-ParkStep_Headingshorter+workclamp_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v01-Test20Reward_251221
- EncodingLatent_col-E-ParkStep_Headingshorter+workclamp_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v01-Test21Reward_251222

**Branches: Heading range (+-0) + no deadzone + workclamp**
- EncodingLatent_col-E-ParkStep_Headingrange0nodeadzone+workclamp_Abl1.0-Actor-popobs_v01-Test25_251227
  - Abl 1 (blind actor).
- EncodingLatent_col-E-ParkStep_Headingrange0nodeadzone+workclamp_Abl2.5-ActorCritic_Privscan_v01-Test25_251227
  - Abl 2.5 (actor raw scandot).
**Reward-scale sweeps (Test20-27).**: **Best** at Test25 so other Abls were conducted with Test25 scale  
- EncodingLatent_col-E-ParkStep_Headingrange0nodeadzone+workclamp_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v01-Test20
- EncodingLatent_col-E-ParkStep_Headingrange0nodeadzone+workclamp_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v01-Test22
- EncodingLatent_col-E-ParkStep_Headingrange0nodeadzone+workclamp_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v01-Test23_251223
- EncodingLatent_col-E-ParkStep_Headingrange0nodeadzone+workclamp_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v01-Test24_251226
- EncodingLatent_col-E-ParkStep_Headingrange0nodeadzone+workclamp_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v01-Test25_251226
- EncodingLatent_col-E-ParkStep_Headingrange0nodeadzone+workclamp_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v01-Test26_251226
- EncodingLatent_col-E-ParkStep_Headingrange0nodeadzone+workclamp_Abl3.5-Actor-ScandotEncoding1_Critic-ScandotEncoding2_v01-Test27_251226
  - Reward-scale sweeps (Test20-27).
- EncodingLatent_col-E-ParkStep_Headingrange0nodeadzone+workclamp_Abl4.0-Actor-ScandotEncoding_Critic-PrivScan_v01-Test25_251228
  - Abl 4.0 (actor encoded scan, critic raw scan).
- EncodingLatent_col-E-ParkStep_Headingrange0nodeadzone+workclamp_Abl7.0-Abl3.5+privobsEncoding_to_Critic_v01-Test25_251228
  - Abl 7.0 (add priv-obs encoding to critic).

-------------------------------------------------------------------------------

## Base branches (not described in PPTs)
- main
  - Default branch.
- 3d
  - 3D method branch (mentioned in top-level README).
- 3d_IK_no_divergence
  - IK stability branch (not detailed in notes).
