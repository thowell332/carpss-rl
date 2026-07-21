#!/usr/bin/env python3
"""Shared experiment utilities for norm-supervised highway experiments.

This module contains code that is common to both the discrete and continuous
supervisor evaluation scripts, including:

- Linear mapping utility
- Episode-level metrics collection
- CSV writing helpers

Environment/model-specific wiring (e.g., which Gym env to create, which RL
algorithm to load, and which concrete supervisor to use) should live in the
individual scripts (e.g. ``test_discrete.py``, ``test_continuous.py``) which
import and reuse the components defined here.
"""

from __future__ import annotations

from typing import Any
import csv
import numpy as np
import os

def lmap(v: float, x: tuple[float, float], y: tuple[float, float]) -> float:
    """Linear map of value ``v`` with input range ``x`` to desired range ``y``."""
    return y[0] + (v - x[0]) * (y[1] - x[0]) / (x[1] - x[0])

BASE_SEED = 239


def episode_seed(base_seed: int, episode: int) -> int:
    """Deterministic per-episode seed, independent of total episode count.

    Episode ``i`` always maps to ``base_seed + i``, so a 100-episode run and a
    1000-episode run share the same initial conditions for overlapping indices.
    """
    return base_seed + episode

class EpisodeMetrics:
    """Collects metrics for a single episode."""

    def __init__(
        self,
        lane_count: int,
        collision_reward: float,
        reward_speed_range: list[float],
        env_config: dict | None = None,
    ):
        self.episode_length = 0
        self.collision = False
        self.speed_history: list[float] = []
        self.cost: float = 0.0          # Weighted norm violation cost
        self.avoided_cost: float = 0.0  # Avoided weighted norm violation cost
        self.expected_cost: float = 0.0  # Expected weighted norm violation cost under policy

        # Reward tracking
        self.cumulative_reward: float = 0.0        # Total reward
        self.cumulative_basic_reward: float = 0.0  # Basic reward component
        self.cumulative_added_reward: float = 0.0  # Added reward component

        # Reward configuration from environment config
        self.env_config: dict[str, Any] = env_config or {}
        self.collision_reward: float = collision_reward
        self.right_lane_reward: float = self.env_config.get("right_lane_reward", 0.0)
        self.high_speed_reward: float = self.env_config.get("high_speed_reward", 0.0)
        self.reward_speed_min: float = reward_speed_range[0]
        self.reward_speed_max: float = reward_speed_range[1]
        self.reward_speed_range: tuple[float, float] = (
            self.reward_speed_min,
            self.reward_speed_max,
        )

        # Supervisor statistics
        self.supervisor_start_idx: int = 0
        self.supervisor_outcome_start_idx: int = 0

    def add_timestep(
        self,
        speed: float,
        lane_index: int,
        cost: float,
        avoided_cost: float,
        vehicle_heading: float,
        num_lanes: int,
        on_road: bool,
        crashed: bool,
        env_unwrapped=None,
        expected_cost: float | None = None,
    ):
        """Add data from a single timestep."""
        self.episode_length += 1
        self.speed_history.append(speed)

        self.cost += cost
        self.avoided_cost += avoided_cost
        if expected_cost is not None:
            self.expected_cost += expected_cost

        # Lane normalization: lane_index / max(num_lanes - 1, 1)
        lane_normalized = lane_index / max(num_lanes - 1, 1)

        # Forward speed: speed * cos(heading)
        forward_speed = speed * np.cos(vehicle_heading)

        # Scaled speed: linear map from reward_speed_range to [0, 1], then clip
        if self.reward_speed_range[1] > self.reward_speed_range[0]:
            scaled_speed = lmap(forward_speed, self.reward_speed_range, (0.0, 1.0))
            scaled_speed = float(np.clip(scaled_speed, 0.0, 1.0))
        else:
            scaled_speed = 1.0 if forward_speed >= self.reward_speed_range[0] else 0.0

        # Compute reward components using environment if available, otherwise manually
        basic_reward = None
        added_reward = None

        if env_unwrapped is not None:
            try:
                # If environment exposes basic_reward and added_reward (ALL variant), use them
                basic_reward = env_unwrapped.basic_reward
                added_reward = env_unwrapped.added_reward
            except AttributeError:
                # Environment doesn't expose these attributes (non-ALL variant)
                pass

        if basic_reward is None or added_reward is None:
            # Compute manually (matching HighwayEnvMEAddRightRewardALL formula)
            # basic_reward = collision + speed + 1 (base reward)
            basic_reward = (
                self.collision_reward * (1.0 if crashed else 0.0)
                + self.high_speed_reward * float(np.clip(scaled_speed, 0.0, 1.0))
                + 1.0  # Base reward (always included in ALL variant basic_reward)
            )
            if not on_road:
                basic_reward = 0.0

            # Added reward: right lane component
            added_reward = self.right_lane_reward * lane_normalized
            if not on_road:
                added_reward = 0.0

        # Total reward: basic + added
        timestep_reward = basic_reward + added_reward

        self.cumulative_reward += timestep_reward
        self.cumulative_basic_reward += basic_reward
        self.cumulative_added_reward += added_reward

    def finalize(self):
        """Finalize metrics at the end of an episode.

        Currently a no-op: all relevant aggregates are updated in add_timestep().
        """
        return

    def get_episode_results(
        self,
        episode_id: int,
        config,
        supervisor_root_results: list,
        supervisor_outcomes: list,
    ) -> dict[str, float]:
        """Get episode results as totals/counts for CSV output."""
        # Calculate mean speed
        mean_speed = float(np.mean(self.speed_history)) if self.speed_history else np.nan

        # Calculate supervisor statistics for this episode
        episode_root_results = supervisor_root_results[self.supervisor_start_idx :]
        # Some steps may not perform a KL solve and return None for root_results.
        # Exclude those when computing iteration and convergence statistics.
        episode_root_results = [
            result for result in episode_root_results if result is not None
        ]
        episode_outcomes = supervisor_outcomes[self.supervisor_outcome_start_idx :]

        # Mean iterations to converge for this episode
        if episode_root_results:
            iterations = [
                result.iterations
                for result in episode_root_results
                if hasattr(result, "iterations")
            ]
            mean_iterations = float(np.mean(iterations)) if iterations else np.nan
        else:
            mean_iterations = np.nan

        # Convergence rate for this episode
        if episode_root_results:
            converged_count = sum(
                1
                for result in episode_root_results
                if hasattr(result, "converged") and result.converged
            )
            # Only count steps where a root-finding attempt was actually made
            convergence_rate = (
                converged_count / len(episode_root_results)
                if episode_root_results
                else 0.0
            )
        else:
            convergence_rate = 0.0

        # Outcome counts for this episode
        outcome_counts = {
            "unchanged": 0,
            "naively_augmented": 0,
            "rcps_augmented": 0,
            "projection": 0,
        }
        for outcome in episode_outcomes:
            if hasattr(outcome, "value"):
                outcome_str = outcome.value
            else:
                outcome_str = str(outcome)
            if outcome_str in outcome_counts:
                outcome_counts[outcome_str] += 1

        # Build results dictionary
        results: dict[str, float] = {
            "episode_id": episode_id,
            "policy_freq": config.model_env["policy_freq"],
            "profile": config.profile,
            "method": config.method,
            # Record whether hard constraints (filter) were enforced, if available on config.
            "filter": getattr(config, "filter", None),
            "value": float(config.value) if getattr(config, "value", None) is not None else np.nan,
            "episode_length": self.episode_length,
            "collision": 1 if self.collision else 0,
            "mean_speed": mean_speed,
            # Cost totals
            "total_cost": self.cost,
            "total_avoided_cost": self.avoided_cost,
            "total_expected_cost": self.expected_cost,
            # Reward totals
            "total_reward": self.cumulative_reward,
            "total_basic_reward": self.cumulative_basic_reward,
            "total_added_reward": self.cumulative_added_reward,
            # Supervisor statistics
            "mean_iterations_to_converge": mean_iterations,
            "convergence_rate": convergence_rate,
            "outcome_unchanged_count": outcome_counts["unchanged"],
            "outcome_naively_augmented_count": outcome_counts["naively_augmented"],
            "outcome_rcps_augmented_count": outcome_counts["rcps_augmented"],
            "outcome_projection_count": outcome_counts["projection"],
        }

        return results


class CSVWriter:
    """Handles CSV file writing with incremental updates."""

    def __init__(self, output_file: str, lane_count: int):
        self.output_file = output_file
        self.lane_count = lane_count
        self.fieldnames = self._get_fieldnames()
        self._create_file()

    def _get_fieldnames(self) -> list[str]:
        """Get CSV field names based on lane count."""
        base_fields = [
            "episode_id",
            "policy_freq",
            "profile",
            "method",
            "filter",
            "value",
            "episode_length",
            "collision",
            "mean_speed",
        ]

        # Add cost and reward totals
        cost_reward_fields = [
            "total_cost",
            "total_avoided_cost",
            "total_expected_cost",
            "total_reward",
            "total_basic_reward",
            "total_added_reward",
        ]

        # Add supervisor statistics fields
        supervisor_fields = [
            "mean_iterations_to_converge",
            "convergence_rate",
            "outcome_unchanged_count",
            "outcome_naively_augmented_count",
            "outcome_rcps_augmented_count",
            "outcome_projection_count",
        ]

        return base_fields + cost_reward_fields + supervisor_fields

    def _create_file(self):
        """Create the CSV file with headers."""
        try:
            # Ensure the directory exists
            directory = os.path.dirname(self.output_file)
            if directory:
                os.makedirs(directory, exist_ok=True)
            with open(self.output_file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
        except Exception as e:  # pragma: no cover - defensive
            raise RuntimeError(f"Failed to create output file {self.output_file}: {e}")

    def write_experiment(self, results: dict[str, float]):
        """Write a single experiment's results to the CSV file."""
        try:
            with open(self.output_file, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writerow(results)
        except Exception as e:  # pragma: no cover - defensive
            raise RuntimeError(f"Failed to write to output file {self.output_file}: {e}")
