#!/usr/bin/env python3
import argparse
import csv
import json
import numpy as np
import os
import sys
from collections import defaultdict

import gymnasium
import torch
from stable_baselines3 import DQN
from highway_env.envs.highway_env import HighwayEnv

from norm_supervisor.consts import VEHICLE_LENGTH, ACTION_STRINGS
from norm_supervisor.norms.norms import TailgatingNorm
from norm_supervisor.supervisor import Supervisor, PolicyAugmentMethod
import norm_supervisor.metrics as metrics

# Configuration mappings
CONFIGS = {
    '4L20V': {
        'model_file': '4_lanes_20_vehicles.zip',
        'env_config': '4_lanes_20_vehicles.json',
        'lanes': 4,
        'policy_freq': 1
    },
    '6L50V': {
        'model_file': '4_lanes_20_vehicles.zip',
        'env_config': '6_lanes_50_vehicles.json',
        'lanes': 5,
        'policy_freq': 1
    }
}

METHOD_MAPPING = {method.value : method for method in PolicyAugmentMethod}

BASE_SEED = 239

class ExperimentConfig:
    """Configuration for experiment parameters."""
    
    def __init__(self, args: argparse.Namespace):
        self.profile = args.profile
        self.env = args.env
        self.method = args.method
        self.value = args.value
        self.num_experiments = args.experiments
        self.num_episodes = args.episodes
        self.output_file = args.output
        self.filter = args.filter
        self.model_env = CONFIGS[self.env]
        
        # Validate configuration
        self._validate()
    
    def _validate(self):
        """Validate the experiment configuration."""
        if self.method in ['adaptive', 'fixed'] and self.value is None:
            raise ValueError("--value is required for adaptive/fixed methods")
        
        # Check if model file exists
        model_path = os.path.join("models", self.model_env['model_file'])
        if not os.path.exists(model_path):
            raise ValueError(f"Model file not found: {model_path}")
        
        # Check if environment config exists
        env_config_path = os.path.join("configs/environment", self.model_env['env_config'])
        if not os.path.exists(env_config_path):
            raise ValueError(f"Environment config not found: {env_config_path}")


class EpisodeMetrics:
    """Collects metrics for a single episode."""
    
    def __init__(self, lane_count: int):
        self.episode_length = 0
        self.collision = False
        self.ttc_history = []
        self.distance_history = []
        self.speed_history = []

        self.lane_times = {f'lane_{i}': 0.0 for i in range(lane_count)}
        
        self.norm_violations            = defaultdict(int)
        self.constraint_violations      = defaultdict(int)
        
        self.cost         = 0.0 # Weighted norm violation cost
        self.avoided_cost = 0.0 # Avoided weighted norm violation cost

        # --- New tracking for unsafe-state behaviour ---
        self.unsafe_frames: int = 0
        # Counts per action id while unsafe
        self.unsafe_action_hist: dict[int, int] = defaultdict(int)

        # Headway derivative while unsafe (per frame)
        self._prev_distance: float | None = None
        self.delta_gap_unsafe_sum: float = 0.0
        self.delta_gap_unsafe_frames: int = 0

        # Minimum gap reached in each unsafe episode
        self.current_min_gap: float | None = None
        self.min_gaps: list[float] = []

        # Duration of each distance-unsafe episode (in frames)
        self.current_unsafe_duration: int = 0
        self.unsafe_durations: list[int] = []

        # --- New tracking for TTC-unsafe behaviour ---
        self.unsafe_ttc_frames: int = 0
        self.unsafe_ttc_action_hist: dict[int, int] = defaultdict(int)
        self._prev_ttc: float | None = None
        self.delta_ttc_unsafe_sum: float = 0.0
        self.delta_ttc_unsafe_frames: int = 0
        self.current_min_ttc: float | None = None
        self.min_ttcs: list[float] = []
        # Duration of each TTC-unsafe episode (in frames)
        self.current_unsafe_ttc_duration: int = 0
        self.unsafe_ttc_durations: list[int] = []
    
    def add_timestep(self, ttc: float, following_distance: float, speed: float, lane_index: int,
                     norm_violations: dict[str, bool], constraint_violations: dict[str, bool],
                     cost: float, avoided_cost: float, action: int):
        """Add data from a single timestep."""
        self.episode_length += 1
        self.ttc_history.append(ttc)
        self.distance_history.append(following_distance)
        self.speed_history.append(speed)
        self.lane_times[f'lane_{lane_index}'] += 1
        
        for norm, flag in norm_violations.items():
            self.norm_violations[norm] += flag
        
        for constraint, flag in constraint_violations.items():
            self.constraint_violations[constraint] += flag
        
        self.cost += cost
        self.avoided_cost += avoided_cost

        # ---------- Unsafe-state bookkeeping ----------
        unsafe = following_distance < 3 * VEHICLE_LENGTH  # Distance criterion
        if unsafe:
            self.unsafe_frames += 1
            self.unsafe_action_hist[action] += 1

            # Count duration frames
            self.current_unsafe_duration += 1

            if self._prev_distance is not None:
                self.delta_gap_unsafe_sum += (following_distance - self._prev_distance)
                self.delta_gap_unsafe_frames += 1

            # Track minimum gap within a contiguous unsafe episode
            if self.current_min_gap is None:
                self.current_min_gap = following_distance
            else:
                self.current_min_gap = min(self.current_min_gap, following_distance)
        else:
            # If exiting an unsafe episode, store the min gap encountered
            if self.current_min_gap is not None:
                self.min_gaps.append(self.current_min_gap)
                self.current_min_gap = None

            # Store duration if we were in an unsafe episode
            if self.current_unsafe_duration > 0:
                self.unsafe_durations.append(self.current_unsafe_duration)
                self.current_unsafe_duration = 0

        self._prev_distance = following_distance

        # ---------- TTC-unsafe bookkeeping ----------
        unsafe_ttc = (not np.isnan(ttc)) and ttc < 3.0
        if unsafe_ttc:
            self.unsafe_ttc_frames += 1
            self.unsafe_ttc_action_hist[action] += 1

            # duration counting
            self.current_unsafe_ttc_duration += 1

            if self._prev_ttc is not None:
                self.delta_ttc_unsafe_sum += (ttc - self._prev_ttc)
                self.delta_ttc_unsafe_frames += 1

            if self.current_min_ttc is None:
                self.current_min_ttc = ttc
            else:
                self.current_min_ttc = min(self.current_min_ttc, ttc)
        else:
            if self.current_min_ttc is not None:
                self.min_ttcs.append(self.current_min_ttc)
                self.current_min_ttc = None

            if self.current_unsafe_ttc_duration > 0:
                self.unsafe_ttc_durations.append(self.current_unsafe_ttc_duration)
                self.current_unsafe_ttc_duration = 0

        self._prev_ttc = ttc

    def finalize(self):
        """Finalize metrics at the end of an episode (capture trailing unsafe segment)."""
        if self.current_min_gap is not None:
            self.min_gaps.append(self.current_min_gap)
            self.current_min_gap = None

        if self.current_unsafe_duration > 0:
            self.unsafe_durations.append(self.current_unsafe_duration)
            self.current_unsafe_duration = 0

        if self.current_min_ttc is not None:
            self.min_ttcs.append(self.current_min_ttc)
            self.current_min_ttc = None

        if self.current_unsafe_ttc_duration > 0:
            self.unsafe_ttc_durations.append(self.current_unsafe_ttc_duration)
            self.current_unsafe_ttc_duration = 0
    
    def _safe_nanmean(self, data):
        """Calculate nanmean safely, avoiding empty slice warnings."""
        if not data or all(np.isnan(x) for x in data):
            return np.nan
        return np.nanmean(data)


class ExperimentResults:
    """Aggregates results across episodes for a single experiment."""
    
    def __init__(self, experiment_id: int, config: ExperimentConfig):
        self.experiment_id = experiment_id
        self.config = config
        self.episode_metrics: list[EpisodeMetrics] = []
    
    def add_episode(self, metrics: EpisodeMetrics):
        """Add metrics from a completed episode."""
        self.episode_metrics.append(metrics)
    
    def get_experiment_results(self) -> dict[str, float]:
        """Calculate mean values across all episodes in this experiment."""
        if not self.episode_metrics:
            return {}
        
        # Aggregate episode data
        episode_lengths = []
        total_collisions = 0
        all_ttc_history, all_distance_history, all_speed_history = [], [], []
        all_lane_times = defaultdict(float)
        all_norm_violations = defaultdict(int)
        all_constraint_violations = defaultdict(int)
        total_cost, total_avoided_cost = 0.0, 0.0

        # Aggregation containers for distance-unsafe metrics
        total_unsafe_frames = 0
        unsafe_action_counts = defaultdict(int)
        total_delta_gap_sum = 0.0
        total_delta_gap_frames = 0
        all_min_gaps: list[float] = []
        all_unsafe_durations: list[int] = []

        # Aggregation containers for TTC-unsafe metrics
        total_unsafe_ttc_frames = 0
        unsafe_ttc_action_counts = defaultdict(int)
        total_delta_ttc_sum = 0.0
        total_delta_ttc_frames = 0
        all_min_ttcs: list[float] = []
        all_unsafe_ttc_durations: list[int] = []

        for ep in self.episode_metrics:
            episode_lengths.append(ep.episode_length)
            total_collisions += ep.collision
            all_ttc_history.extend(ep.ttc_history)
            all_distance_history.extend(ep.distance_history)
            all_speed_history.extend(ep.speed_history)
            for lane, time in ep.lane_times.items():
                all_lane_times[lane] += time
            for norm, count in ep.norm_violations.items():
                all_norm_violations[norm] += count
            for constraint, count in ep.constraint_violations.items():
                all_constraint_violations[constraint] += count
            total_cost += ep.cost
            total_avoided_cost += ep.avoided_cost

            # Aggregate new unsafe metrics
            total_unsafe_frames += ep.unsafe_frames
            for a, c in ep.unsafe_action_hist.items():
                unsafe_action_counts[a] += c
            total_delta_gap_sum += ep.delta_gap_unsafe_sum
            total_delta_gap_frames += ep.delta_gap_unsafe_frames
            all_min_gaps.extend(ep.min_gaps)

            all_unsafe_durations.extend(ep.unsafe_durations)

            # TTC metrics aggregation
            total_unsafe_ttc_frames += ep.unsafe_ttc_frames
            for a, c in ep.unsafe_ttc_action_hist.items():
                unsafe_ttc_action_counts[a] += c
            total_delta_ttc_sum += ep.delta_ttc_unsafe_sum
            total_delta_ttc_frames += ep.delta_ttc_unsafe_frames
            all_min_ttcs.extend(ep.min_ttcs)
            all_unsafe_ttc_durations.extend(ep.unsafe_ttc_durations)

        # Calculate time exposed TTC and following distance
        sample_frequency = self.config.model_env['policy_freq']
        total_time = sum(episode_lengths)

        # Mean recovery time in seconds
        if all_unsafe_durations:
            mean_recovery_time = np.mean(all_unsafe_durations) / self.config.model_env['policy_freq']
        else:
            mean_recovery_time = np.nan

        ttc_1s = metrics.calculate_exposure(all_ttc_history, sample_frequency, 1) / total_time
        ttc_2s = metrics.calculate_exposure(all_ttc_history, sample_frequency, 2) / total_time
        ttc_3s = metrics.calculate_exposure(all_ttc_history, sample_frequency, 3) / total_time
        distance_1v = metrics.calculate_exposure(all_distance_history, sample_frequency, 1 * VEHICLE_LENGTH) / total_time
        distance_2v = metrics.calculate_exposure(all_distance_history, sample_frequency, 2 * VEHICLE_LENGTH) / total_time
        distance_3v = metrics.calculate_exposure(all_distance_history, sample_frequency, 3 * VEHICLE_LENGTH) / total_time

        # Normalize lane preferences, violation rates, and cost rates
        lane_preferences, norm_violation_rates, constraint_violation_rates = {}, {}, {}
        for lane, time in all_lane_times.items():
            lane_preferences[lane] = time / total_time
        for norm, count in all_norm_violations.items():
            norm_violation_rates[norm] = count / total_time
        for constraint, count in all_constraint_violations.items():
            constraint_violation_rates[constraint] = count / total_time
        cost_rate = total_cost / total_time
        avoided_cost_rate = total_avoided_cost / total_time

        # ----- Compute new unsafe behaviour metrics -----
        if total_unsafe_frames > 0:
            unsafe_slow_rate = unsafe_action_counts.get(ACTION_STRINGS["SLOWER"], 0) / total_unsafe_frames

            lane_left_id  = ACTION_STRINGS["LANE_LEFT"]
            lane_right_id = ACTION_STRINGS["LANE_RIGHT"]
            unsafe_lane_rate = (
                unsafe_action_counts.get(lane_left_id, 0) +
                unsafe_action_counts.get(lane_right_id, 0)
            ) / total_unsafe_frames

            unsafe_faster_rate = unsafe_action_counts.get(ACTION_STRINGS["FASTER"], 0) / total_unsafe_frames
            unsafe_idle_rate   = unsafe_action_counts.get(ACTION_STRINGS["IDLE"], 0)   / total_unsafe_frames
        else:
            unsafe_slow_rate   = np.nan
            unsafe_lane_rate   = np.nan
            unsafe_faster_rate = np.nan
            unsafe_idle_rate   = np.nan

        mean_delta_gap_unsafe = (
            total_delta_gap_sum / total_delta_gap_frames
        ) if total_delta_gap_frames > 0 else np.nan

        min_gap_p05 = (
            np.percentile(all_min_gaps, 5) if all_min_gaps else np.nan
        )

        # ----- TTC unsafe behaviour metrics -----
        if total_unsafe_ttc_frames > 0:
            unsafe_ttc_slow_rate = unsafe_ttc_action_counts.get(ACTION_STRINGS["SLOWER"], 0) / total_unsafe_ttc_frames
            lane_left_id  = ACTION_STRINGS["LANE_LEFT"]
            lane_right_id = ACTION_STRINGS["LANE_RIGHT"]
            unsafe_ttc_lane_rate = (
                unsafe_ttc_action_counts.get(lane_left_id, 0) +
                unsafe_ttc_action_counts.get(lane_right_id, 0)
            ) / total_unsafe_ttc_frames

            unsafe_ttc_faster_rate = unsafe_ttc_action_counts.get(ACTION_STRINGS["FASTER"], 0) / total_unsafe_ttc_frames
            unsafe_ttc_idle_rate   = unsafe_ttc_action_counts.get(ACTION_STRINGS["IDLE"], 0)   / total_unsafe_ttc_frames
        else:
            unsafe_ttc_slow_rate   = np.nan
            unsafe_ttc_lane_rate   = np.nan
            unsafe_ttc_faster_rate = np.nan
            unsafe_ttc_idle_rate   = np.nan

        mean_delta_ttc_unsafe = (
            total_delta_ttc_sum / total_delta_ttc_frames
        ) if total_delta_ttc_frames > 0 else np.nan

        min_ttc_p05 = (
            np.percentile(all_min_ttcs, 5) if all_min_ttcs else np.nan
        )

        # Mean TTC recovery time
        if all_unsafe_ttc_durations:
            mean_ttc_recovery_time = np.mean(all_unsafe_ttc_durations) / self.config.model_env['policy_freq']
        else:
            mean_ttc_recovery_time = np.nan

        # Build base results
        results = {
            'experiment_id': self.experiment_id,
            'policy_freq': self.config.model_env['policy_freq'],
            'profile': self.config.profile,
            'method': self.config.method,
            'value': float(self.config.value) if self.config.value is not None else np.nan,
            'num_episodes': len(self.episode_metrics),
            'mean_episode_length': np.mean(episode_lengths),
            'total_collisions': total_collisions,
            'tet_1s': ttc_1s,
            'tet_2s': ttc_2s,
            'tet_3s': ttc_3s,
            'teud_1v': distance_1v,
            'teud_2v': distance_2v,
            'teud_3v': distance_3v,
            'mean_speed': np.mean(all_speed_history),
            'speed_violation_rate': norm_violation_rates.get('SpeedNorm', np.nan),
            'tailgating_violation_rate': norm_violation_rates.get('TailgatingNorm', np.nan),
            'braking_violation_rate': norm_violation_rates.get('BrakingNorm', np.nan),
            'lane_keeping_violation_rate': norm_violation_rates.get('LaneKeepingNorm', np.nan),
            'lane_change_tailgating_violation_rate': norm_violation_rates.get('LaneChangeTailgatingNorm', np.nan),
            'lane_change_braking_violation_rate': norm_violation_rates.get('LaneChangeBrakingNorm', np.nan),
            'collision_violation_rate': constraint_violation_rates.get('CollisionConstraint', np.nan),
            'lane_change_collision_violation_rate': constraint_violation_rates.get('LaneChangeCollisionConstraint', np.nan),
            'safety_envelope_violation_rate': constraint_violation_rates.get('SafetyEnvelopeConstraint', np.nan),
            'lane_change_safety_envelope_violation_rate': constraint_violation_rates.get('LaneChangeSafetyEnvelopeConstraint', np.nan),
            'cost_rate': cost_rate,
            'avoided_cost_rate': avoided_cost_rate,
            'unsafe_slow_rate': unsafe_slow_rate,
            'unsafe_lane_rate': unsafe_lane_rate,
            'unsafe_faster_rate': unsafe_faster_rate,
            'unsafe_idle_rate': unsafe_idle_rate,
            'mean_delta_gap_unsafe': mean_delta_gap_unsafe,
            'min_gap_p05': min_gap_p05,
            'unsafe_ttc_slow_rate': unsafe_ttc_slow_rate,
            'unsafe_ttc_lane_rate': unsafe_ttc_lane_rate,
            'unsafe_ttc_faster_rate': unsafe_ttc_faster_rate,
            'unsafe_ttc_idle_rate': unsafe_ttc_idle_rate,
            'mean_delta_ttc_unsafe': mean_delta_ttc_unsafe,
            'min_ttc_p05': min_ttc_p05,
            'mean_recovery_time': mean_recovery_time,
            'mean_ttc_recovery_time': mean_ttc_recovery_time,
        }
        
        # Add lane preferences based on actual lane count
        for i in range(self.config.model_env['lanes']):
            results[f'lane_{i}_preference'] = lane_preferences.get(f'lane_{i}', 0.0)
        
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
            'experiment_id', 'policy_freq', 'profile', 'method', 'value', 'num_episodes',
            'mean_episode_length', 'total_collisions', 'tet_1s', 'tet_2s', 'tet_3s', 'teud_1v',
            'teud_2v', 'teud_3v', 'mean_speed'
        ]
        
        # Add lane fields
        lane_fields = [f'lane_{i}_preference' for i in range(self.lane_count)]
        
        # Add violation fields
        violation_fields = [
            'speed_violation_rate', 'tailgating_violation_rate',  'braking_violation_rate',
            'lane_keeping_violation_rate', 'lane_change_tailgating_violation_rate',
            'lane_change_braking_violation_rate', 'collision_violation_rate',
            'lane_change_collision_violation_rate', 'safety_envelope_violation_rate',
            'lane_change_safety_envelope_violation_rate', 'cost_rate', 'avoided_cost_rate',
            'unsafe_slow_rate', 'unsafe_lane_rate', 'unsafe_faster_rate', 'unsafe_idle_rate',
            'mean_delta_gap_unsafe', 'min_gap_p05',
            'unsafe_ttc_slow_rate', 'unsafe_ttc_lane_rate', 'unsafe_ttc_faster_rate', 'unsafe_ttc_idle_rate',
            'mean_delta_ttc_unsafe', 'min_ttc_p05', 'mean_recovery_time', 'mean_ttc_recovery_time'
        ]
        
        return base_fields + lane_fields + violation_fields
    
    def _create_file(self):
        """Create the CSV file with headers."""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            with open(self.output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
        except Exception as e:
            raise RuntimeError(f"Failed to create output file {self.output_file}: {e}")
    
    def write_experiment(self, results: dict[str, float]):
        """Write a single experiment's results to the CSV file."""
        try:
            with open(self.output_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writerow(results)
        except Exception as e:
            raise RuntimeError(f"Failed to write to output file {self.output_file}: {e}")


class ExperimentRunner:
    """Main experiment runner class."""
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.lane_count = self.config.model_env['lanes']
        self.csv_writer = CSVWriter(config.output_file, self.lane_count)
        
        # Load model and environment config
        self.model = self._load_model()
        self.env_config = self._load_env_config()
    
    def _load_model(self) -> DQN:
        """Load the DQN model."""
        # Check if CUDA is available and set device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        model_path = os.path.join("models", self.config.model_env['model_file'])
        print(f"Loading model from {model_path}...")
        model = DQN.load(model_path, device=device)
        model.set_random_seed(BASE_SEED)
        return model
    
    def _load_env_config(self) -> dict:
        """Load environment configuration."""
        env_config_path = os.path.join("configs/environment", self.config.model_env['env_config'])
        print(f"Loading environment config from {env_config_path}...")
        with open(env_config_path, 'r') as f:
            return json.load(f)
    
    def _create_supervisor(self, env: HighwayEnv) -> Supervisor:
        """Create supervisor with appropriate configuration."""
        supervisor_method = METHOD_MAPPING[self.config.method].value
        fixed_beta = self.config.value if self.config.method == 'fixed' else None
        kl_budget = self.config.value if self.config.method == 'adaptive' else None
        
        return Supervisor(
            env=env,
            profile_name=self.config.profile,
            filter=self.config.filter,
            method=supervisor_method,
            fixed_beta=fixed_beta,
            kl_budget=kl_budget,
            verbose=False
        )
    
    def run_experiment(self, experiment_id: int) -> ExperimentResults:
        """Run a single experiment."""
        print(f"\nStarting experiment {experiment_id + 1}/{self.config.num_experiments}")
        
        # Create environment
        env = gymnasium.make("highway-fast-v0", render_mode="rgb_array", config=self.env_config)
        env_unwrapped: HighwayEnv = env.unwrapped
        
        # Create supervisor
        supervisor = self._create_supervisor(env_unwrapped)
        
        # Create results container
        results = ExperimentResults(experiment_id, self.config)
        
        # Run episodes
        for episode in range(self.config.num_episodes):
            episode_seed = BASE_SEED * (10 ** len(str(abs(self.config.num_experiments)))) + experiment_id
            episode_seed = episode_seed * (10 ** len(str(abs(self.config.num_episodes)))) + episode
            
            obs, _ = env.reset(seed=episode_seed)
            supervisor.reset_norms()
            
            # Create metrics collector for this episode
            episode_metrics = EpisodeMetrics(self.lane_count)
            
            done = truncated = False
            while not (done or truncated):
                # Get model action
                action, _ = self.model.predict(obs, deterministic=True)
                action = action.item()
                
                # Count norm violations for original action
                violations_dict = supervisor.count_norm_violations(action)
                violations_weight_dict = supervisor.weight_norm_violations(violations_dict)
                violations_weight = sum(violations_weight_dict.values())
                
                # Count constraint violations for original action
                constraint_violations_dict = supervisor.count_constraint_violations(action)
                
                # Apply supervisor if needed
                if self.config.method != 'nop' or self.config.filter:
                    new_action = supervisor.decide_action(self.model, obs)
                    new_violations_dict = supervisor.count_norm_violations(new_action)
                    new_violations_weight_dict = supervisor.weight_norm_violations(new_violations_dict)
                    new_violations_weight = sum(new_violations_weight_dict.values())

                    new_constraint_violations_dict = supervisor.count_constraint_violations(new_action)
                    
                    avoided_violations_weight = violations_weight - new_violations_weight
                    action = new_action

                    # Set measures to the values for the new action
                    violations_dict = new_violations_dict
                    violations_weight_dict = new_violations_weight_dict
                    violations_weight = new_violations_weight
                    constraint_violations_dict = new_constraint_violations_dict
                else:
                    avoided_violations_weight = 0.0
                
                # Calculate metrics
                ttcs = metrics.calculate_neighbour_ttcs(env_unwrapped.vehicle)
                ttc = ttcs[0] if ttcs[0] != np.inf else np.nan
                following_distance = TailgatingNorm.evaluate_criterion(env_unwrapped.vehicle)
                following_distance = following_distance if following_distance != np.inf else np.nan
                speed = env_unwrapped.vehicle.speed
                _, _, lane_index = env_unwrapped.vehicle.lane_index
                
                # Add timestep data
                episode_metrics.add_timestep(
                    ttc=ttc,
                    following_distance=following_distance,
                    speed=speed,
                    lane_index=lane_index,
                    norm_violations=violations_dict,
                    constraint_violations=constraint_violations_dict,
                    cost=violations_weight,
                    avoided_cost=avoided_violations_weight,
                    action=action
                )
                
                # Take action
                obs, _, done, truncated, info = env.step(action)
                
                # Check for collision
                if done or truncated:
                    if info.get("crashed", False):
                        print(f"*** CRASHED WITH SEED {episode_seed} ***")
                        episode_metrics.collision = True
            
            # Finalize episode metrics
            episode_metrics.finalize()
            results.add_episode(episode_metrics)
            
            # Print progress every 10 episodes
            if (episode + 1) % 10 == 0:
                print(f"  Completed episode {episode + 1}/{self.config.num_episodes}")
        
        env.close()
        return results
    
    def run_all_experiments(self):
        """Run all experiments and write results incrementally."""
        print(f"Starting experimental run:")
        print(f"  Profile: {self.config.profile}")
        print(f"  Method: {self.config.method}")
        print(f"  Value: {self.config.value or 'N/A'}")
        print(f"  Model: {self.config.model_env['model_file']}")
        print(f"  Environment: {self.config.model_env['env_config']}")
        print(f"  Experiments: {self.config.num_experiments}")
        print(f"  Episodes per experiment: {self.config.num_episodes}")
        print(f"  Output: {self.config.output_file}")
        
        # Use the output file path as provided by the shell script
        # The shell script already creates the proper directory structure
        print(f"Results will be written to: {self.config.output_file}")
        
        for experiment_id in range(self.config.num_experiments):
            try:
                results = self.run_experiment(experiment_id)
                experiment_results = results.get_experiment_results()
                self.csv_writer.write_experiment(experiment_results)
                print(f"Experiment {experiment_id + 1} completed:")
                print(f"  Collisions: {experiment_results['total_collisions']}")
                print(f"  Cost Rate: {experiment_results['cost_rate']:.3f}")
            except Exception as e:
                import traceback
                print(f"Error in experiment {experiment_id + 1}: {e}")
                print(f"Full traceback:")
                traceback.print_exc()
                raise
        print(f"\nAll experiments completed. Results written to {self.csv_writer.output_file}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run norm-supervised highway driving experiments",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('--profile', choices=[p for p in Supervisor.PROFILES], required=True,
                       help='Driving profile to use')
    parser.add_argument('--method', choices=['nop', 'naive', 'adaptive', 'fixed', 'projection'], 
                       required=True, help='Supervisor method')
    parser.add_argument('--env', choices=[e for e in CONFIGS], default='4L20V',
                       help='Environment/model configuration')
    parser.add_argument('--value', type=float, 
                       help='Value for adaptive/fixed methods (required for adaptive/fixed methods)')
    parser.add_argument('--experiments', type=int, default=5,
                       help='Number of experiments to run')
    parser.add_argument('--episodes', type=int, default=100,
                       help='Number of episodes per experiment')
    parser.add_argument('--output', required=True,
                       help='Output CSV file path')
    parser.add_argument('--filter', dest='filter', action='store_true',
                       help='Enable supervisor filtering (default: True)')
    parser.add_argument('--no-filter', dest='filter', action='store_false',
                       help='Disable supervisor filtering')
    parser.set_defaults(filter=True)
    
    args = parser.parse_args()
    
    # Validate method and value for adaptive/fixed methods
    if args.method in ['adaptive', 'fixed'] and args.value is None:
        parser.error("--value is required for adaptive/fixed methods")
    
    return args


def main():
    """Main function."""
    try:
        args = parse_arguments()
        config = ExperimentConfig(args)
        runner = ExperimentRunner(config)
        runner.run_all_experiments()
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        print(f"Full traceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
