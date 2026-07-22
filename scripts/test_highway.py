#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path

# Add project root to path BEFORE importing highway_env to ensure local version is used
script_dir = Path(__file__).parent
project_root = script_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import gymnasium
import torch
from stable_baselines3 import DQN, DQN_ME

# Import custom highway_env to register environments
# This must be imported after adding project root to path
import highway_env  # noqa: F401  # This imports highway_env.envs which registers environments
from highway_env.envs.highway_env import HighwayEnv

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
    '2L10V': {
        'model_file': '4_lanes_20_vehicles.zip',
        'env_config': '2_lanes_10_vehicles.json',
        'lanes': 2,
        'policy_freq': 1
    },
    # Special configuration for direct comparison with the original Residual Q-learning experiment
    '3L30V': {
        'model_file': '3_lanes_30_vehicles.zip',
        'env_config': '3_lanes_30_vehicles.json',
        'lanes': 3,
        'policy_freq': 1
    },
    '4L40V': {
        'model_file': '3_lanes_30_vehicles.zip',
        'env_config': '4_lanes_40_vehicles.json',
        'lanes': 4,
        'policy_freq': 1
    },
    '4L20V': {
        'model_file': '4_lanes_20_vehicles.zip',
        'env_config': '4_lanes_20_vehicles.json',
        'lanes': 4,
        'policy_freq': 1
    },
    '6L50V': {
        'model_file': '4_lanes_20_vehicles.zip',
        'env_config': '6_lanes_50_vehicles.json',
        'lanes': 6,
        'policy_freq': 1
    }
}


class HighwayCSVWriter(CSVWriter):
    """CSV writer that additionally records lane preference for highway experiments."""

    def __init__(self, output_file: str, lane_count: int):
        self.lane_count = lane_count
        super().__init__(output_file, lane_count)

    def _get_fieldnames(self) -> list[str]:
        base_fields = super()._get_fieldnames()
        lane_fields = [f"lane_{i}_time" for i in range(self.lane_count)]
        return base_fields + lane_fields

class ExperimentConfig:
    """Configuration for experiment parameters."""
    
    def __init__(self, args: argparse.Namespace):
        self.profile = args.profile
        self.env = args.env
        self.method = args.method
        self.value = args.value
        self.filter = args.filter
        self.num_episodes = args.episodes
        self.output_file = args.output
        self.seed = args.seed
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


class ExperimentRunner:
    """Main experiment runner class."""
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.lane_count = self.config.model_env['lanes']
        self.csv_writer = HighwayCSVWriter(config.output_file, self.lane_count)
        
        # Load model and environment config
        self.model = self._load_model()
        self.env_config = self._load_env_config()
    
    def _load_model(self) -> DQN:
        """Load the DQN model (supports both DQN and DQN_ME)."""
        # Check if CUDA is available and set device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {device}")
        
        model_path = os.path.join("models", self.config.model_env['model_file'])
        print(f"Loading model from {model_path}...")
        
        # Try to load as DQN_ME first (if available), then fall back to DQN
        if DQN_ME is not None:
            try:
                model = DQN_ME.load(model_path, device=device)
                print("Loaded model as DQN_ME")
                model.set_random_seed(self.config.seed)
                return model
            except Exception as e:
                print(f"Could not load as DQN_ME, trying DQN... ({e})")
        
        # Fall back to standard DQN
        model = DQN.load(model_path, device=device)
        print("Loaded model as DQN")
        model.set_random_seed(self.config.seed)
        return model
    
    def _load_env_config(self) -> dict:
        """Load environment configuration."""
        env_config_path = os.path.join("configs/environment", self.config.model_env['env_config'])
        print(f"Loading environment config from {env_config_path}...")
        with open(env_config_path, 'r') as f:
            return json.load(f)
    
    def _create_supervisor(self, env: HighwayEnv) -> AbstractSupervisor:
        """Create discrete supervisor with appropriate configuration."""
        fixed_beta = self.config.value if self.config.method == 'fixed' else None
        kl_budget = self.config.value if self.config.method == 'adaptive' else None

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
    
    def run_all_episodes(self):
        """Run all episodes and write results incrementally (one row per episode)."""
        print(f"Starting experimental run:")
        print(f"  Profile: {self.config.profile}")
        print(f"  Method: {self.config.method}")
        print(f"  Value: {self.config.value or 'N/A'}")
        print(f"  Enforce constraints (filter): {self.config.filter}")
        print(f"  Model: {self.config.model_env['model_file']}")
        print(f"  Environment: {self.config.model_env['env_config']}")
        print(f"  Episodes: {self.config.num_episodes}")
        print(f"  Base seed: {self.config.seed}")
        print(f"  Output: {self.config.output_file}")
        
        # Create environment using custom HighwayEnvMEAddRightReward
        # This environment exposes basic_reward and added_reward attributes
        # Note: render_mode is not supported in the custom highway_env, so we omit it
        env = gymnasium.make("highway-ME-basic-AddRightRewardALL-v0")
        env_unwrapped: HighwayEnv = env.unwrapped

        # Override the default highway configuration with the loaded JSON config
        # so that lanes_count, vehicles_count, rewards, etc. match the selected setup.
        env_unwrapped.configure(self.env_config)
        
        # Create supervisor
        supervisor = self._create_supervisor(env_unwrapped)
        
        # Extract reward configuration from environment config
        collision_reward = self.env_config.get('collision_reward', -1)
        reward_speed_range = self.env_config.get('reward_speed_range', [20, 30])
        
        # Run episodes
        policy_period = self.config.model_env.get('policy_freq', 1)
        for episode in range(self.config.num_episodes):
            ep_seed = episode_seed(self.config.seed, episode)
            
            obs, _ = env.reset(seed=ep_seed)
            supervisor.reset_norms()
            
            # Track supervisor history indices at start of episode
            supervisor_start_idx = len(supervisor.root_results_history)
            supervisor_outcome_start_idx = len(supervisor.outcome_history)
            
            # Create metrics collector for this episode
            episode_metrics = EpisodeMetrics(
                self.lane_count,
                collision_reward=collision_reward,
                reward_speed_range=reward_speed_range,
                env_config=self.env_config
            )
            episode_metrics.supervisor_start_idx = supervisor_start_idx
            episode_metrics.supervisor_outcome_start_idx = supervisor_outcome_start_idx
            
            done = truncated = False

            # Track time spent in each lane for this episode
            # Keys match the CSV columns (`lane_i_time`)
            lane_times = {f"lane_{i}_time": 0.0 for i in range(self.lane_count)}
            while not (done or truncated):
                # Get base model action
                base_action, _ = self.model.predict(obs, deterministic=True)
                base_action = int(base_action.item())

                # Calculate aggregated norm-violation cost for original action
                base_norm_violation_costs = supervisor.calculate_norm_violation_costs(
                    base_action
                )
                base_weighted_cost = sum(
                    base_norm_violation_costs[n] * supervisor.norm_weights[n]
                    for n in base_norm_violation_costs
                )

                # Apply supervisor if needed and compute updated cost
                if self.config.method != 'nop':
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
                else:
                    action = base_action
                    norm_violation_costs = base_norm_violation_costs
                    violations_weight = base_weighted_cost
                    avoided_violations_weight = 0.0

                # Compute expected norm violation cost under the base model policy
                with torch.no_grad():
                    obs_tensor, _ = self.model.policy.obs_to_tensor(obs)
                    q_values = self.model.q_net(obs_tensor)
                    action_probs = torch.softmax(q_values, dim=-1)[0].detach().cpu().numpy()
                cost_vector = supervisor.get_norm_violation_cost(supervisor.ACTIONS_ALL).detach().cpu().numpy()
                expected_cost = float((action_probs * cost_vector).sum())
                
                # Calculate metrics
                speed = env_unwrapped.vehicle.speed
                _, _, lane_index = env_unwrapped.vehicle.lane_index
                heading = env_unwrapped.vehicle.heading
                num_lanes = len(env_unwrapped.road.network.all_side_lanes(env_unwrapped.vehicle.lane_index))
                on_road = env_unwrapped.vehicle.on_road
                crashed = env_unwrapped.vehicle.crashed

                # Accumulate lane occupancy time (in same units as episode_length * policy_period)
                lane_key = f"lane_{lane_index}_time"
                if lane_key in lane_times:
                    lane_times[lane_key] += policy_period
                
                # Add timestep data
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
                )
                
                # Take action
                obs, _, done, truncated, info = env.step(action)
                
                # Check for collision
                if done or truncated:
                    if info.get("crashed", False):
                        print(f"*** CRASHED WITH SEED {ep_seed} ***")
                        episode_metrics.collision = True
            
            # Finalize episode metrics
            episode_metrics.finalize()
            
            # Get episode results and write to CSV
            episode_results = episode_metrics.get_episode_results(
                episode_id=episode,
                config=self.config,
                supervisor_root_results=supervisor.root_results_history,
                supervisor_outcomes=supervisor.outcome_history
            )

            # Add lane preference metrics (time spent in each lane)
            for i in range(self.lane_count):
                key = f"lane_{i}_time"
                episode_results[key] = lane_times.get(key, 0.0)

            self.csv_writer.write_experiment(episode_results)
            
            # Print progress every 10 episodes
            if (episode + 1) % 10 == 0:
                print(f"  Completed episode {episode + 1}/{self.config.num_episodes}")
        
        env.close()
        print(f"\nAll episodes completed. Results written to {self.csv_writer.output_file}")
    

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run norm-supervised highway driving experiments",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--profile',
        choices=[p for p in DiscreteSupervisor.PROFILES],
        required=True,
        help='Driving profile to use',
    )
    parser.add_argument(
        '--method',
        choices=[m.value for m in PolicyAugmentMethod],
        required=True,
        help='Supervisor method',
    )
    parser.add_argument(
        '--filter',
        action='store_true',
        help='Enforce hard constraints by filtering impermissible actions',
    )
    parser.add_argument('--env', choices=[e for e in CONFIGS], default='4L20V',
                       help='Environment/model configuration')
    parser.add_argument('--value', type=float, 
                       help='Value for adaptive/fixed methods (required for adaptive/fixed methods)')
    parser.add_argument('--episodes', type=int, default=1000,
                       help='Number of episodes to run')
    parser.add_argument(
        '--seed',
        type=int,
        default=BASE_SEED,
        help=f'Base random seed (default {BASE_SEED}). Episode i uses seed + i.',
    )
    parser.add_argument('--output', required=True,
                       help='Output CSV file path')
    args = parser.parse_args()
    
    # Validate method and value for adaptive/fixed methods
    if args.method in ['adaptive', 'fixed'] and args.value is None:
        parser.error("--value is required for adaptive/fixed methods")
    
    return args


def main():
    """Main function to run norm-supervised highway driving experiments.
    
    Parses command line arguments, creates experiment configuration, and runs all experiments
    with the specified parameters.
    """
    try:
        args = parse_arguments()
        config = ExperimentConfig(args)
        runner = ExperimentRunner(config)
        runner.run_all_episodes()
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        print(f"Full traceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
