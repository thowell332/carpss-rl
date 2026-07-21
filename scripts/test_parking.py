#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

# Add project root to path BEFORE importing highway_env to ensure local version is used
script_dir = Path(__file__).parent
project_root = script_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import gymnasium as gym
import torch
from stable_baselines3 import SAC

from highway_env.envs.parking_env import ParkingVectorlizedEnvBoundaryCostALL

from supervisor import ContinuousSupervisor, PolicyAugmentMethod

from scripts.base_experiment import (
    BASE_SEED,
    CSVWriter,
    EpisodeMetrics,
    episode_seed,
)


class ParkingCSVWriter(CSVWriter):
    """CSV writer that additionally records parking-specific metrics."""

    def _get_fieldnames(self) -> list[str]:
        base_fields = super()._get_fieldnames()
        # Parking-specific episode-level indicators:
        # - boundary_touched: whether parking boundary lines were contacted
        # - parking_success: whether the episode succeeded in parking
        return base_fields + ["boundary_touched", "parking_success"]


class ParkingExperimentConfig:
    """Configuration for parking experiment parameters."""

    def __init__(self, args: argparse.Namespace):
        self.profile = "clean_parking"
        self.method = args.method
        self.value = args.value
        self.filter = args.filter
        self.num_episodes = args.episodes
        self.output_file = args.output
        self.model_path = args.model_path

        # Model/env metadata for logging
        self.model_env = {
            "model_file": os.path.basename(self.model_path),
            "lanes": 1,
            "policy_freq": 1,
        }

        self._validate()

    def _validate(self):
        """Validate the experiment configuration."""
        if self.method in ["adaptive", "fixed"] and self.value is None:
            raise ValueError("--value is required for adaptive/fixed methods")

        if not os.path.exists(self.model_path):
            raise ValueError(f"Model file not found: {self.model_path}")


class ParkingExperimentRunner:
    """Run norm-supervised experiments in the parking environment."""

    def __init__(self, config: ParkingExperimentConfig):
        self.config = config
        self.lane_count = self.config.model_env["lanes"]
        self.csv_writer = ParkingCSVWriter(config.output_file, self.lane_count)
        self.model = self._load_model()

    def _load_model(self) -> SAC:
        """Load a SAC model for the continuous parking env."""
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {device}")
        print(f"Loading SAC model from {self.config.model_path}...")
        model = SAC.load(self.config.model_path, device=device)
        model.set_random_seed(BASE_SEED)
        return model

    def _create_supervisor(self, env_unwrapped: ParkingVectorlizedEnvBoundaryCostALL) -> ContinuousSupervisor:
        """Create a continuous supervisor with the clean parking profile."""
        fixed_beta = self.config.value if self.config.method == "fixed" else None
        kl_budget = self.config.value if self.config.method == "adaptive" else None

        supervisor = ContinuousSupervisor(
            env=env_unwrapped,
            profile_name=self.config.profile,
            method=self.config.method,
            enforce_constraints=self.config.filter,
            fixed_beta=fixed_beta,
            kl_budget=kl_budget,
            device=self.model.device,
            verbose=False,
        )

        # Record actual policy frequency for logging
        try:
            self.config.model_env["policy_freq"] = float(env_unwrapped.config["policy_frequency"])
        except Exception:
            self.config.model_env["policy_freq"] = 1

        return supervisor

    def run_all_episodes(self):
        """Run all episodes and write results incrementally (one row per episode)."""
        print("Starting parking experiment:")
        print(f"  Profile: {self.config.profile}")
        print(f"  Method: {self.config.method}")
        print(f"  Value: {self.config.value or 'N/A'}")
        print(f"  Enforce constraints (filter): {self.config.filter}")
        print(f"  Model: {self.config.model_path}")
        print(f"  Episodes: {self.config.num_episodes}")
        print(f"  Output: {self.config.output_file}")

        env = gym.make('parking-basic-boundaryall-v0')
        env_unwrapped: ParkingVectorlizedEnvBoundaryCostALL = env.unwrapped

        supervisor = self._create_supervisor(env_unwrapped)

        for episode in range(self.config.num_episodes):
            ep_seed = episode_seed(BASE_SEED, episode)
            obs, _ = env.reset(seed=ep_seed)
            supervisor.reset_norms()

            # Track supervisor history indices at start of episode
            supervisor_start_idx = len(supervisor.root_results_history)
            supervisor_outcome_start_idx = len(supervisor.outcome_history)

            # Use generic reward config; actual ALL env exposes basic_reward/added_reward
            episode_metrics = EpisodeMetrics(
                self.lane_count,
                collision_reward=-1.0,
                reward_speed_range=[0.0, 10.0],
                env_config=self.config.model_env,
            )
            episode_metrics.supervisor_start_idx = supervisor_start_idx
            episode_metrics.supervisor_outcome_start_idx = supervisor_outcome_start_idx

            done = False
            truncated = False

            # Track whether parking boundary lines were touched during this episode
            boundary_touched = False
            # Track whether the episode ended in a successful parking maneuver
            parking_success = False

            while not (done or truncated):
                # Base SAC action
                base_action, _ = self.model.predict(obs, deterministic=True)

                # Cost of base action
                base_costs_dict = supervisor.calculate_norm_violation_costs(base_action)
                base_weighted_cost = sum(
                    base_costs_dict[n] * supervisor.norm_weights[n]
                    for n in base_costs_dict
                )

                # Apply supervisor if needed
                if self.config.method != "nop":
                    supervised_action = supervisor.predict(self.model, obs)
                    costs_dict = supervisor.calculate_norm_violation_costs(supervised_action)
                    weighted_cost = sum(
                        costs_dict[n] * supervisor.norm_weights[n] for n in costs_dict
                    )
                    avoided = base_weighted_cost - weighted_cost
                    action = supervised_action
                    violations_weight = weighted_cost
                    avoided_violations_weight = avoided
                else:
                    action = base_action
                    violations_weight = base_weighted_cost
                    avoided_violations_weight = 0.0

                # Extract simple kinematic data for metrics; parking has a single ego vehicle
                vehicle = env_unwrapped.controlled_vehicles[0]
                speed = getattr(vehicle, "speed", 0.0)
                heading = getattr(vehicle, "heading", 0.0)
                on_road = getattr(vehicle, "on_road", True)
                crashed = getattr(vehicle, "crashed", False)

                # Parking layout does not use lane-based driving, so we treat it as single-lane
                lane_index = 0
                num_lanes = 1

                # Check if parking boundary lines are touched at this timestep
                if env_unwrapped.boundary_collision_checking():
                    boundary_touched = True

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
                )

                # Step environment
                obs, _, done, truncated, info = env.step(action)

                # Track whether the environment reports a successful parking outcome
                if info.get("is_success", False):
                    parking_success = True

                # Mark collision at end of episode if reported by env
                if done or truncated:
                    if info.get("crashed", False):
                        episode_metrics.collision = True

            episode_metrics.finalize()

            episode_results = episode_metrics.get_episode_results(
                episode_id=episode,
                config=self.config,
                supervisor_root_results=supervisor.root_results_history,
                supervisor_outcomes=supervisor.outcome_history,
            )

            # Add episode-level indicators for parking-specific outcomes
            episode_results["boundary_touched"] = 1 if boundary_touched else 0
            episode_results["parking_success"] = 1 if parking_success else 0

            self.csv_writer.write_experiment(episode_results)

            if (episode + 1) % 10 == 0:
                print(f"  Completed episode {episode + 1}/{self.config.num_episodes}")

        env.close()
        print(f"\nAll episodes completed. Results written to {self.csv_writer.output_file}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run norm-supervised parking experiments with clean parking profile",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
        "--value",
        type=float,
        help="Value for adaptive/fixed methods (required for adaptive/fixed methods)",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=100,
        help="Number of episodes to run",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV file path",
    )
    parser.add_argument(
        "--model-path",
        required=True,
        help="Path to SAC model .zip file for the parking env",
    )

    args = parser.parse_args()

    if args.method in ["adaptive", "fixed"] and args.value is None:
        parser.error("--value is required for adaptive/fixed methods")

    return args


def main():
    """Main entry point."""
    try:
        args = parse_arguments()
        config = ParkingExperimentConfig(args)
        runner = ParkingExperimentRunner(config)
        runner.run_all_episodes()
    except Exception as e:
        import traceback

        print(f"Error: {e}")
        print("Full traceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
