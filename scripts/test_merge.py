#!/usr/bin/env python3
"""Run norm-supervised SCPS experiments on the merge environment."""

import argparse
import json
import os
import sys
from pathlib import Path

# Headless frame dumps must set the video driver before pygame is imported.
# Do NOT set this for --render (human GUI needs a real display).
if "--render-dir" in sys.argv:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("OFFSCREEN_RENDERING", "1")
    # Dummy + a stale/unreachable DISPLAY (common on WSL) can hang in pygame;
    # offscreen rgb_array rendering does not need a window server.
    os.environ.pop("DISPLAY", None)
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

# Add project root to path BEFORE importing highway_env to ensure local version is used
script_dir = Path(__file__).parent
project_root = script_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import gym
import gymnasium
import numpy as np
import torch
from stable_baselines3 import DQN, DQN_ME

# Import custom highway_env to register environments
import highway_env  # noqa: F401
from highway_env.envs.merge_env import MergeEnv
from highway_env.envs.merge_courtesy import (
    DEFAULT_COURTESY_DISTANCE,
    courtesy_add_on_reward,
    courtesy_gate_gap,
)

from supervisor import DiscreteSupervisor, PolicyAugmentMethod
from supervisor.abstract import AbstractSupervisor

from scripts.base_experiment import (
    BASE_SEED,
    CSVWriter,
    EpisodeMetrics,
    episode_seed,
)

# Configuration mappings
CONFIGS = {
    # Default merge-ME-basic setup (matches RQL-Comparison merge_basic training).
    "MERGE_BASIC": {
        "model_file": "merge_basic.zip",
        "env_config": "merge_basic.json",
        "basic_reward_config": "merge_basic_reward.json",
        "gym_id": "merge-ME-basic-v0",
        "lanes": 2,
        "policy_freq": 1,
    },
}


class MergeCSVWriter(CSVWriter):
    """CSV writer for merge experiments: lane times + courtesy-gap metric."""

    def __init__(self, output_file: str, lane_count: int):
        self.lane_count = lane_count
        super().__init__(output_file, lane_count)

    def _get_fieldnames(self) -> list[str]:
        base_fields = super()._get_fieldnames()
        lane_fields = [f"lane_{i}_time" for i in range(self.lane_count)]
        # Mean courtesy-gap violation [m] while gate is active; NaN if never active.
        # Violation = max(0, threshold - gap): 0 when gap exceeds the envelope.
        courtesy_fields = ["mean_courtesy_gap_violation", "courtesy_active_steps"]
        return base_fields + lane_fields + courtesy_fields


class ExperimentConfig:
    """Configuration for merge experiment parameters."""

    def __init__(self, args: argparse.Namespace):
        self.profile = args.profile
        self.env = args.env
        self.method = args.method
        self.value = args.value
        self.filter = args.filter
        self.num_episodes = args.episodes
        self.output_file = args.output
        self.seed = args.seed
        self.debug = bool(getattr(args, "debug", False))
        self.render = bool(getattr(args, "render", False))
        self.render_dir = getattr(args, "render_dir", None)
        self.model_env = dict(CONFIGS[self.env])
        if args.model_path:
            # Allow overriding the default models/<file> location (e.g. Drive checkpoint).
            model_path = Path(args.model_path)
            if model_path.is_dir():
                model_path = model_path / "model.zip"
            self.model_env["model_path"] = str(model_path)
        self._validate()

    def _validate(self):
        """Validate the experiment configuration."""
        if self.method in ["adaptive", "fixed"] and self.value is None:
            raise ValueError("--value is required for adaptive/fixed methods")

        model_path = self.model_env.get(
            "model_path",
            os.path.join("models", self.model_env["model_file"]),
        )
        if not os.path.exists(model_path):
            raise ValueError(f"Model file not found: {model_path}")

        env_config_path = os.path.join(
            "configs/environment", self.model_env["env_config"]
        )
        if not os.path.exists(env_config_path):
            raise ValueError(f"Environment config not found: {env_config_path}")

        basic_reward_path = os.path.join(
            "configs/environment", self.model_env["basic_reward_config"]
        )
        if not os.path.exists(basic_reward_path):
            raise ValueError(f"Basic reward config not found: {basic_reward_path}")

        if self.render_dir:
            Path(self.render_dir).mkdir(parents=True, exist_ok=True)

class ExperimentRunner:
    """Main merge experiment runner class."""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.lane_count = self.config.model_env["lanes"]
        self.csv_writer = MergeCSVWriter(config.output_file, self.lane_count)

        self.env_config = self._load_env_config()
        self.model = self._load_model()

    def _resolve_model_path(self) -> str:
        if "model_path" in self.config.model_env:
            return self.config.model_env["model_path"]
        return os.path.join("models", self.config.model_env["model_file"])

    def _gym_space_custom_objects(self) -> dict:
        """Build gym.spaces stand-ins for SB3 load when pickled spaces fail.

        Checkpoints trained under a different gym build often cannot unpickle
        ``action_space`` / ``observation_space`` (e.g. missing
        ``RandomNumberGenerator._generator_ctor``). The vendored DQN_ME also
        requires ``gym.spaces`` (not gymnasium.spaces) at construction time.
        """
        probe = gymnasium.make(self.config.model_env["gym_id"])
        try:
            if self.env_config:
                probe.unwrapped.configure(self.env_config)
            obs_shape = probe.observation_space.shape
            n_actions = int(probe.action_space.n)
        finally:
            probe.close()

        return {
            "observation_space": gym.spaces.Box(
                low=-np.inf,
                high=np.inf,
                shape=obs_shape,
                dtype=np.float32,
            ),
            "action_space": gym.spaces.Discrete(n_actions),
        }

    def _load_model(self) -> DQN:
        """Load the DQN model (supports both DQN and DQN_ME)."""
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {device}")

        model_path = self._resolve_model_path()
        print(f"Loading model from {model_path}...")

        custom_objects = self._gym_space_custom_objects()
        loaders = []
        if DQN_ME is not None:
            loaders.append(("DQN_ME", DQN_ME))
        loaders.append(("DQN", DQN))

        last_error: Exception | None = None
        for name, cls in loaders:
            # Prefer a clean load; fall back to gym.spaces custom_objects on
            # gym/gymnasium pickle mismatches (not missing checkpoint files).
            for use_custom in (False, True):
                try:
                    kwargs = {"device": device}
                    if use_custom:
                        kwargs["custom_objects"] = custom_objects
                    model = cls.load(model_path, **kwargs)
                    suffix = " (with gym.spaces custom_objects)" if use_custom else ""
                    print(f"Loaded model as {name}{suffix}")
                    model.set_random_seed(self.config.seed)
                    return model
                except Exception as e:
                    last_error = e
                    if not use_custom:
                        print(
                            f"Could not load as {name} without custom_objects "
                            f"({e}); retrying with gym.spaces stand-ins..."
                        )
            print(f"Could not load as {name}: {last_error}")

        raise RuntimeError(
            f"Failed to load model from {model_path}. Last error: {last_error}"
        )

    def _load_env_config(self) -> dict:
        """Load environment configuration."""
        env_config_path = os.path.join(
            "configs/environment", self.config.model_env["env_config"]
        )
        print(f"Loading environment config from {env_config_path}...")
        with open(env_config_path, "r") as f:
            return json.load(f)

    def _load_basic_reward_config(self) -> dict:
        """Load merge_basic training reward coeffs for metric logging."""
        basic_reward_path = os.path.join(
            "configs/environment", self.config.model_env["basic_reward_config"]
        )
        print(f"Loading basic reward config from {basic_reward_path}...")
        with open(basic_reward_path, "r") as handle:
            config = json.load(handle)
        return {
            key: value
            for key, value in config.items()
            if not str(key).startswith("_")
        }

    def _create_supervisor(self, env: MergeEnv) -> AbstractSupervisor:
        """Create discrete supervisor with appropriate configuration."""
        fixed_beta = self.config.value if self.config.method == "fixed" else None
        kl_budget = self.config.value if self.config.method == "adaptive" else None

        return DiscreteSupervisor(
            env=env,
            profile_name=self.config.profile,
            method=self.config.method,
            enforce_constraints=self.config.filter,
            fixed_beta=fixed_beta,
            kl_budget=kl_budget,
            device=self.model.device,
            verbose=False,
        )

    def _courtesy_debug_snapshot(self, supervisor: AbstractSupervisor, vehicle) -> dict:
        """Collect merge-courtesy geometry / cost diagnostics for one step."""
        action_names = DiscreteSupervisor.ACTIONS_ALL
        cost_vec = (
            supervisor.get_norm_violation_cost(action_names).detach().cpu().numpy()
        )
        courtesy = next(
            (n for n in supervisor.norms if str(n) == "MergeCourtesyNorm"), None
        )
        mergers = courtesy._merging_vehicles(vehicle) if courtesy is not None else []
        gap = None
        merger_lane = None
        behind = None
        if courtesy is not None and mergers:
            merger = mergers[0]
            merger_lane = merger.lane_index
            try:
                lane = vehicle.road.network.get_lane(
                    (
                        vehicle.lane_index[0],
                        vehicle.lane_index[1],
                        courtesy.target_lane_id,
                    )
                )
                s_ego, _ = lane.local_coordinates(vehicle.position)
                s_merge, _ = lane.local_coordinates(merger.position)
                gap = (s_merge - merger.LENGTH / 2.0) - (
                    s_ego + vehicle.LENGTH / 2.0
                )
                behind = bool(s_ego < s_merge)
            except KeyError:
                pass
        return {
            "cost_vec": cost_vec,
            "n_mergers": len(mergers),
            "merger_lane": merger_lane,
            "gap": gap,
            "behind": behind,
            "ego_lane": vehicle.lane_index,
            "action_names": action_names,
        }

    def run_all_episodes(self):
        """Run all episodes and write results incrementally (one row per episode)."""
        print("Starting experimental run:")
        print(f"  Profile: {self.config.profile}")
        print(f"  Method: {self.config.method}")
        print(f"  Value: {self.config.value or 'N/A'}")
        print(f"  Enforce constraints (filter): {self.config.filter}")
        print(f"  Model: {self._resolve_model_path()}")
        print(f"  Environment: {self.config.model_env['env_config']}")
        print(f"  Gym ID: {self.config.model_env['gym_id']}")
        print(f"  Episodes: {self.config.num_episodes}")
        print(f"  Base seed: {self.config.seed}")
        print(f"  Output: {self.config.output_file}")
        print(f"  Debug: {self.config.debug}")
        print(f"  Render: {self.config.render} dir={self.config.render_dir}")

        render_mode = None
        if self.config.render or self.config.render_dir:
            # This highway_env fork uses env.render(mode=...), not gymnasium render_mode.
            render_mode = "human" if self.config.render and not self.config.render_dir else "rgb_array"

        env = gymnasium.make(self.config.model_env["gym_id"])
        env_unwrapped: MergeEnv = env.unwrapped
        env_unwrapped.configure(self.env_config)
        if self.config.render_dir:
            env_unwrapped.config["offscreen_rendering"] = True
            env_unwrapped.config["render_agent"] = True
            env_unwrapped.config["show_trajectories"] = False
        elif self.config.render:
            env_unwrapped.config["offscreen_rendering"] = False
            env_unwrapped.config["render_agent"] = True
            env_unwrapped.config["real_time_rendering"] = True

        supervisor = self._create_supervisor(env_unwrapped)

        basic_reward_config = self._load_basic_reward_config()
        collision_reward = basic_reward_config.get("collision_reward", -0.5)
        reward_speed_range = basic_reward_config.get("reward_speed_range", [20, 30])

        policy_period = self.config.model_env.get("policy_freq", 1)
        debug_stats = {
            "steps": 0,
            "action_changed": 0,
            "norm_active": 0,  # max cost_vec > 0
            "realized_cost_pos": 0,
            "outcomes": {},
        }

        for episode in range(self.config.num_episodes):
            ep_seed = episode_seed(self.config.seed, episode)

            obs, _ = env.reset(seed=ep_seed)
            supervisor.reset_norms()

            supervisor_start_idx = len(supervisor.root_results_history)
            supervisor_outcome_start_idx = len(supervisor.outcome_history)

            episode_metrics = EpisodeMetrics(
                self.lane_count,
                collision_reward=collision_reward,
                reward_speed_range=reward_speed_range,
                env_config=self.env_config,
                basic_reward_config=basic_reward_config,
            )
            episode_metrics.supervisor_start_idx = supervisor_start_idx
            episode_metrics.supervisor_outcome_start_idx = supervisor_outcome_start_idx

            done = truncated = False
            lane_times = {f"lane_{i}_time": 0.0 for i in range(self.lane_count)}
            courtesy_gap_violations: list[float] = []
            courtesy_norm = next(
                (n for n in supervisor.norms if str(n) == "MergeCourtesyNorm"),
                None,
            )
            courtesy_target_lane = (
                int(courtesy_norm.target_lane_id) if courtesy_norm is not None else 1
            )
            if courtesy_norm is not None:
                courtesy_threshold = float(courtesy_norm.courtesy_distance)
            else:
                courtesy_threshold = float(DEFAULT_COURTESY_DISTANCE)
            step_idx = 0

            while not (done or truncated):
                base_action, _ = self.model.predict(obs, deterministic=True)
                base_action = int(base_action.item())

                base_norm_violation_costs = supervisor.calculate_norm_violation_costs(
                    base_action
                )
                base_weighted_cost = sum(
                    base_norm_violation_costs[n] * supervisor.norm_weights[n]
                    for n in base_norm_violation_costs
                )

                # Use supervisor whenever shaping or hard filtering is requested.
                # (Filter-only = method nop + --filter must still call predict/decide.)
                if self.config.method != "nop" or self.config.filter:
                    supervised_action = int(supervisor.predict(self.model, obs))
                    norm_violation_costs = supervisor.calculate_norm_violation_costs(
                        supervised_action
                    )
                    weighted_cost = sum(
                        norm_violation_costs[n] * supervisor.norm_weights[n]
                        for n in norm_violation_costs
                    )
                    avoided_violations_weight = base_weighted_cost - weighted_cost
                    action = supervised_action
                    violations_weight = weighted_cost
                    outcome = (
                        supervisor.outcome_history[-1]
                        if supervisor.outcome_history
                        else None
                    )
                else:
                    action = base_action
                    norm_violation_costs = base_norm_violation_costs
                    violations_weight = base_weighted_cost
                    avoided_violations_weight = 0.0
                    outcome = None

                with torch.no_grad():
                    obs_tensor, _ = self.model.policy.obs_to_tensor(obs)
                    q_values = self.model.q_net(obs_tensor)
                    action_probs = (
                        torch.softmax(q_values, dim=-1)[0].detach().cpu().numpy()
                    )
                cost_vector = (
                    supervisor.get_norm_violation_cost(supervisor.ACTIONS_ALL)
                    .detach()
                    .cpu()
                    .numpy()
                )
                expected_cost = float((action_probs * cost_vector).sum())

                if self.config.debug or self.config.render_dir:
                    snap = self._courtesy_debug_snapshot(
                        supervisor, env_unwrapped.vehicle
                    )
                    debug_stats["steps"] += 1
                    if action != base_action:
                        debug_stats["action_changed"] += 1
                    if float(np.max(snap["cost_vec"])) > 0:
                        debug_stats["norm_active"] += 1
                    if violations_weight > 0:
                        debug_stats["realized_cost_pos"] += 1
                    if outcome is not None:
                        key = getattr(outcome, "value", str(outcome))
                        debug_stats["outcomes"][key] = (
                            debug_stats["outcomes"].get(key, 0) + 1
                        )

                if self.config.debug:
                    names = DiscreteSupervisor.ACTIONS_ALL
                    cost_str = " ".join(
                        f"{names[i]}={cost_vector[i]:.2f}" for i in range(len(names))
                    )
                    gap = snap["gap"]
                    gap_str = f"{gap:.1f}m" if gap is not None else "n/a"
                    print(
                        f"[ep={episode} t={step_idx}] "
                        f"ego={snap['ego_lane']} merger={snap['merger_lane']} "
                        f"gap={gap_str} behind={snap['behind']} "
                        f"n_mergers={snap['n_mergers']}"
                    )
                    print(
                        f"  base={names[base_action]} action={names[action]} "
                        f"changed={action != base_action} "
                        f"outcome={getattr(outcome, 'value', None)} "
                        f"realized={violations_weight:.3f} E[c]={expected_cost:.3f}"
                    )
                    print(f"  costs[{cost_str}]")

                if self.config.render or self.config.render_dir:
                    # --render needs a real display; --render-dir can use dummy SDL.
                    if self.config.render and not os.environ.get("DISPLAY"):
                        print(
                            "WARNING: --render needs a display (DISPLAY is unset). "
                            "On WSL use WSLg/an X server, or pass --render-dir for PNGs."
                        )
                        self.config.render = False
                    elif (
                        self.config.render_dir
                        and not os.environ.get("DISPLAY")
                        and os.environ.get("SDL_VIDEODRIVER") != "dummy"
                    ):
                        print(
                            "WARNING: skipping frames (--render-dir) without DISPLAY. "
                            "Start with SDL_VIDEODRIVER=dummy, or use --debug only."
                        )
                        self.config.render_dir = None

                    if self.config.render or self.config.render_dir:
                        try:
                            frame = env_unwrapped.render(mode=render_mode or "rgb_array")
                        except Exception as exc:
                            print(f"WARNING: rendering disabled after failure: {exc}")
                            self.config.render = False
                            self.config.render_dir = None
                            frame = None
                        else:
                            if self.config.render_dir is not None and frame is not None:
                                try:
                                    from PIL import Image
                                except ImportError as exc:
                                    raise RuntimeError(
                                        "Saving render frames requires Pillow (`pip install pillow`)."
                                    ) from exc
                                out = (
                                    Path(self.config.render_dir)
                                    / f"ep{episode:03d}_t{step_idx:03d}.png"
                                )
                                Image.fromarray(frame).save(out)

                speed = env_unwrapped.vehicle.speed
                _, _, lane_index = env_unwrapped.vehicle.lane_index
                heading = env_unwrapped.vehicle.heading
                num_lanes = len(
                    env_unwrapped.road.network.all_side_lanes(
                        env_unwrapped.vehicle.lane_index
                    )
                )
                on_road = env_unwrapped.vehicle.on_road
                crashed = env_unwrapped.vehicle.crashed

                lane_key = f"lane_{lane_index}_time"
                if lane_key in lane_times:
                    lane_times[lane_key] += policy_period

                gap = courtesy_gate_gap(
                    env_unwrapped.vehicle,
                    target_lane_id=courtesy_target_lane,
                )
                if gap is not None:
                    # Positive shortfall inside the courtesy envelope; 0 otherwise.
                    courtesy_gap_violations.append(
                        max(0.0, courtesy_threshold - float(gap))
                    )

                # Residual add-on dual of the courtesy norm: -sqrt(x) from actual gap.
                courtesy_added = courtesy_add_on_reward(
                    env_unwrapped.vehicle,
                    courtesy_distance=courtesy_threshold,
                    target_lane_id=courtesy_target_lane,
                )

                episode_metrics.add_timestep(
                    speed=speed,
                    lane_index=lane_index,
                    cost=violations_weight,
                    avoided_cost=avoided_violations_weight,
                    vehicle_heading=heading,
                    num_lanes=num_lanes,
                    on_road=on_road,
                    crashed=crashed,
                    env_unwrapped=env_unwrapped,
                    expected_cost=expected_cost,
                    added_reward=courtesy_added,
                )

                obs, _, done, truncated, info = env.step(action)
                step_idx += 1

                if done or truncated:
                    if info.get("crashed", False):
                        print(f"*** CRASHED WITH SEED {ep_seed} ***")
                        episode_metrics.collision = True

            episode_metrics.finalize()

            episode_results = episode_metrics.get_episode_results(
                episode_id=episode,
                config=self.config,
                supervisor_root_results=supervisor.root_results_history,
                supervisor_outcomes=supervisor.outcome_history,
            )

            for i in range(self.lane_count):
                key = f"lane_{i}_time"
                episode_results[key] = lane_times.get(key, 0.0)

            episode_results["courtesy_active_steps"] = len(courtesy_gap_violations)
            episode_results["mean_courtesy_gap_violation"] = (
                float(np.mean(courtesy_gap_violations))
                if courtesy_gap_violations
                else float("nan")
            )

            self.csv_writer.write_experiment(episode_results)

            if (episode + 1) % 10 == 0:
                print(f"  Completed episode {episode + 1}/{self.config.num_episodes}")

        env.close()
        if self.config.debug:
            print("\n=== DEBUG SUMMARY ===")
            print(f"  steps: {debug_stats['steps']}")
            print(
                f"  steps with courtesy cost>0 on some action: "
                f"{debug_stats['norm_active']}"
            )
            print(
                f"  steps where supervised action != base: "
                f"{debug_stats['action_changed']}"
            )
            print(
                f"  steps with realized cost>0: "
                f"{debug_stats['realized_cost_pos']}"
            )
            print(f"  outcomes: {debug_stats['outcomes']}")
        print(
            f"\nAll episodes completed. Results written to {self.csv_writer.output_file}"
        )


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run norm-supervised merge driving experiments",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--profile",
        choices=[p for p in DiscreteSupervisor.PROFILES],
        default="merge_courtesy",
        help="Driving profile to use",
    )
    parser.add_argument(
        "--method",
        choices=[m.value for m in PolicyAugmentMethod],
        required=True,
        help="Supervisor method",
    )
    parser.add_argument(
        "--filter",
        action="store_true",
        help="Enforce hard constraints by filtering impermissible actions",
    )
    parser.add_argument(
        "--env",
        choices=[e for e in CONFIGS],
        default="MERGE_BASIC",
        help="Environment/model configuration",
    )
    parser.add_argument(
        "--value",
        type=float,
        help="Value for adaptive/fixed methods (required for adaptive/fixed methods)",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=1000,
        help="Number of episodes to run",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=BASE_SEED,
        help=f"Base random seed (default {BASE_SEED}). Episode i uses seed + i.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV file path",
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default=None,
        help=(
            "Optional model.zip path or directory containing model.zip. "
            "Overrides models/<CONFIG model_file>."
        ),
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print per-step courtesy/SCPS diagnostics (costs, gap, base vs shaped action)",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Render with render_mode=human (requires a display)",
    )
    parser.add_argument(
        "--render-dir",
        type=str,
        default=None,
        help="Save rgb_array frames as PNGs in this directory (headless-friendly)",
    )
    args = parser.parse_args()

    if args.method in ["adaptive", "fixed"] and args.value is None:
        parser.error("--value is required for adaptive/fixed methods")

    return args


def main():
    """Main function to run norm-supervised merge driving experiments."""
    try:
        args = parse_arguments()
        config = ExperimentConfig(args)
        runner = ExperimentRunner(config)
        runner.run_all_episodes()
    except Exception as e:
        import traceback

        print(f"Error: {e}")
        print("Full traceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
