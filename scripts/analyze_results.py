#!/usr/bin/env python3
"""
Analysis script for norm supervisor experiment results.

Scans CSV files in results directory and generates summary statistics.
"""

import os
import pandas as pd
import numpy as np
from collections import defaultdict
from pathlib import Path
import argparse

import matplotlib


def _configure_plotting_backend(use_latex_pgf: bool = False) -> None:
    """Configure Matplotlib. Use Agg for table-only runs; pgf/LaTeX only when plotting."""
    if use_latex_pgf:
        matplotlib.use("pgf")
        import matplotlib.pyplot as plt

        plt.rcParams.update({
            "text.usetex": True,
            "pgf.texsystem": "pdflatex",
            "pgf.rcfonts": False,
            "font.family": "serif",
            "text.latex.preamble": r"\usepackage{times}",
        })
        return

    matplotlib.use(os.environ.get("MPLBACKEND", "Agg"))


# Default to a headless non-LaTeX backend so Colab / table-only analysis works.
_configure_plotting_backend(use_latex_pgf=False)
import matplotlib.pyplot as plt

colors = {
    "gray": "#949494",
    "medium_gray": "#949494",
    "dark_gray": "#474747",
    "purple": "#542c5d",
    "teal": "#008381"
}


def list_csv_files(directory):
    """List all CSV files in the given directory and subdirectories, skipping any 'ignore' directories.
    
    :param directory: Directory to search for CSV files.
    :return: Sorted list of relative CSV file paths.
    """
    if not os.path.exists(directory):
        return []
    csv_files = []
    for root, dirs, files in os.walk(directory):
        if 'ignore' in dirs:
            dirs.remove('ignore')
        if os.path.basename(root) == 'ignore':
            continue
        for file in files:
            if file.endswith('.csv'):
                rel_path = os.path.relpath(os.path.join(root, file), directory)
                csv_files.append(rel_path)
    return sorted(csv_files)


def parse_configuration_from_filename(filename, results_dir=None):
    """Parse configuration from result path and CSV stem.

    Preferred layout (used by run_experiments*.sh)::

        <domain>/<env>/<profile>/<method>[_filtered|_unfiltered]/<stem>.csv

    where ``domain`` is ``highway`` or ``merge``. Legacy layouts without the
    domain prefix are still accepted::

        <env>/<profile>/<method>/<stem>.csv

    When ``results_dir`` already points at the ``<env>`` folder, paths are only
    ``<profile>/<method>/<stem>.csv``; the env name is taken from ``results_dir``.

    The CSV stem is ``<label>`` or ``<label>_<value>`` where ``value`` is a float
    (e.g. ``3L30V_3L30V_0.05`` or ``MERGE_MERGE_BASIC_0.05``).

    :param filename: Path to the CSV file (relative to the results root).
    :param results_dir: Results root passed to the analyzer (optional).
    :return: Dictionary with parsed configuration fields.
    """
    path = Path(filename)
    method_dir = path.parent.name
    profile = path.parent.parent.name

    DOMAIN_DIRS = {"highway", "merge"}
    env_from_dir = None
    # results/<domain>/<env>/<profile>/<method>/file.csv
    if len(path.parts) >= 5 and path.parts[0] in DOMAIN_DIRS:
        env_from_dir = path.parts[1]
    # results/<env>/<profile>/<method>/file.csv (legacy) or
    # results/<domain>/<env>/... when results_dir is the domain folder
    elif len(path.parts) >= 4:
        env_from_dir = path.parts[0]
    # results_dir is already the env folder → profile/method/file.csv
    if env_from_dir is None and results_dir is not None and len(path.parts) == 3:
        root_name = Path(results_dir).resolve().name
        if root_name and root_name not in {".", "results", *DOMAIN_DIRS}:
            env_from_dir = root_name

    method_base = method_dir
    filter_status = None
    if method_dir.endswith("_filtered"):
        method_base = method_dir[: -len("_filtered")]
        filter_status = "filtered"
    elif method_dir.endswith("_unfiltered"):
        method_base = method_dir[: -len("_unfiltered")]
        filter_status = "unfiltered"

    # Peel trailing numeric hyperparameter from the stem when present.
    stem = path.stem
    value = None
    label = stem
    if "_" in stem:
        head, tail = stem.rsplit("_", 1)
        try:
            value = float(tail)
            label = head
        except ValueError:
            pass

    if env_from_dir is not None:
        model = env_from_dir
        env = env_from_dir
    elif "_" in label:
        # Legacy flat naming: model_env[_value].csv
        model, env = label.split("_", 1)
    else:
        model = env = label

    return {
        "profile": profile,
        "method": method_base,
        "value": value,
        "model": model,
        "env": env,
        "mode": method_base if method_base in ["default", "naive", "nop"] else "default",
        "filter": filter_status,
        "filename": filename,
    }


def load_and_group_data(results_dir):
    """Load all per-episode CSV files, aggregate, and group by configuration.
    
    :param results_dir: Directory containing result CSV files.
    :return: Dictionary mapping configuration tuples to lists of DataFrames.
    """
    csv_files = list_csv_files(results_dir)
    if not csv_files:
        print(f"No CSV files found in '{results_dir}'")
        return {}
    grouped_data = defaultdict(list)

    def _aggregate_episode_level_df(df):
        """Aggregate per-episode dataframe into per-experiment metrics.
        
        This produces a single-row dataframe with the columns expected by the
        rest of the analysis code, including:
        - num_episodes, mean_episode_length, total_collisions, mean_speed
        - lane_i_preference from lane_i_time
        - *_violation_rate from *_violation_count
        - cost_rate, avoided_cost_rate from total_cost / total_avoided_cost
        - unsafe_*_rate / unsafe_ttc_*_rate from *_count columns
        """
        # Basic aggregates
        num_episodes = len(df)
        policy_period = df['policy_freq'].iloc[0] if 'policy_freq' in df.columns else 1.0
        # Treat episode_length as measured in the same units as policy_period
        total_time = float((df['episode_length'] * policy_period).sum())
        mean_episode_length = float(df['episode_length'].mean()) if num_episodes > 0 else np.nan
        total_collisions = float(df['collision'].sum()) if 'collision' in df.columns else np.nan
        mean_speed = float(df['mean_speed'].mean()) if 'mean_speed' in df.columns else np.nan

        out = {
            'num_episodes': num_episodes,
            'mean_episode_length': mean_episode_length,
            'total_collisions': total_collisions,
            'mean_speed': mean_speed,
        }

        # Lane occupancy preferences: normalise lane_i_time by total time,
        # and compute the mean/std of the normalised lane index across episodes.
        lane_time_cols = [c for c in df.columns if c.startswith('lane_') and c.endswith('_time')]
        if total_time > 0 and lane_time_cols:
            lane_indices = [
                int(col[len('lane_') : -len('_time')]) for col in lane_time_cols
            ]
            # Episode-aggregated lane preferences (for compatibility with prior code)
            for col in lane_time_cols:
                lane_idx = int(col[len('lane_') : -len('_time')])
                pref_col = f'lane_{lane_idx}_preference'
                lane_time = float(df[col].sum())
                out[pref_col] = lane_time / total_time

            # Per-episode normalised lane index values
            max_idx = max(lane_indices) if lane_indices else 0
            denom = max_idx if max_idx > 0 else 1  # avoid division by zero for single-lane cases
            norm_lane_values = []
            for _, row in df.iterrows():
                ep_len = row.get('episode_length', 0.0)
                ep_total_time = ep_len * policy_period
                if ep_total_time <= 0:
                    continue
                ep_norm_lane = 0.0
                for lane_idx in lane_indices:
                    time_col = f'lane_{lane_idx}_time'
                    lane_time_ep = float(row.get(time_col, 0.0))
                    p_i = lane_time_ep / ep_total_time
                    ep_norm_lane += (lane_idx / denom) * p_i
                norm_lane_values.append(ep_norm_lane)

            if norm_lane_values:
                out['mean_normalized_lane_index'] = float(np.mean(norm_lane_values))
                # Std over episodes (per configuration)
                out['std_normalized_lane_index_episodes'] = float(np.std(norm_lane_values, ddof=1)) if len(norm_lane_values) > 1 else 0.0

        # Violation rates (per second of simulated time)
        violation_count_cols = [c for c in df.columns if c.endswith('_violation_count')]
        if total_time > 0:
            for col in violation_count_cols:
                base = col[:-len('_violation_count')]
                rate_col = f'{base}_violation_rate'
                total_viol = float(df[col].sum())
                out[rate_col] = total_viol / total_time

        # Cost and avoided-cost rates, plus per-episode mean/std total cost
        if 'total_cost' in df.columns:
            if total_time > 0:
                total_cost = float(df['total_cost'].sum())
                out['cost_rate'] = total_cost / total_time
            # Mean/std realised norm cost per episode
            out['mean_total_cost'] = float(df['total_cost'].mean())
            out['std_total_cost_episodes'] = float(df['total_cost'].std(ddof=1)) if num_episodes > 1 else 0.0
        # Expected norm cost (per-episode means/stds)
        if 'total_expected_cost' in df.columns:
            out['mean_total_expected_cost'] = float(df['total_expected_cost'].mean())
            out['std_total_expected_cost_episodes'] = float(df['total_expected_cost'].std(ddof=1)) if num_episodes > 1 else 0.0
        if 'total_avoided_cost' in df.columns and total_time > 0:
            total_avoided_cost = float(df['total_avoided_cost'].sum())
            out['avoided_cost_rate'] = total_avoided_cost / total_time

        # Reward, basic-reward and added-reward (per-episode means/stds)
        # These are the per-episode aggregates across all episodes in an experiment.
        if 'total_reward' in df.columns:
            out['mean_total_reward'] = float(df['total_reward'].mean())
            out['std_total_reward_episodes'] = (
                float(df['total_reward'].std(ddof=1)) if num_episodes > 1 else 0.0
            )
        if 'total_basic_reward' in df.columns:
            out['mean_basic_reward'] = float(df['total_basic_reward'].mean())
            out['std_basic_reward_episodes'] = float(df['total_basic_reward'].std(ddof=1)) if num_episodes > 1 else 0.0
        if 'total_added_reward' in df.columns:
            out['mean_added_reward'] = float(df['total_added_reward'].mean())
            out['std_added_reward_episodes'] = float(df['total_added_reward'].std(ddof=1)) if num_episodes > 1 else 0.0

        # Merge courtesy gap violation (optional; present only in merge courtesy runs).
        # CSVs store the mean over *active-gate* steps only. Reweight by the fraction
        # of the episode the gate was active so inactive steps count as 0:
        #   full_episode = mean_active * (active_steps / episode_length)
        if 'mean_courtesy_gap_violation' in df.columns:
            if (
                'courtesy_active_steps' in df.columns
                and 'episode_length' in df.columns
            ):
                active = df['courtesy_active_steps'].astype(float)
                lengths = df['episode_length'].astype(float)
                active_mean = df['mean_courtesy_gap_violation'].astype(float)
                frac = np.where(lengths > 0, active / lengths, 0.0)
                # NaN active-mean (never engaged) → 0 contribution over the episode.
                episode_means = np.where(
                    np.isfinite(active_mean),
                    active_mean * frac,
                    0.0,
                )
                # If active_steps is 0, force 0 even if a stale mean is present.
                episode_means = np.where(active > 0, episode_means, 0.0)
                out['mean_courtesy_gap_violation'] = float(np.mean(episode_means))
                out['std_courtesy_gap_violation_episodes'] = (
                    float(np.std(episode_means, ddof=1)) if num_episodes > 1 else 0.0
                )
            else:
                out['mean_courtesy_gap_violation'] = float(
                    df['mean_courtesy_gap_violation'].mean()
                )
                out['std_courtesy_gap_violation_episodes'] = (
                    float(df['mean_courtesy_gap_violation'].std(ddof=1))
                    if num_episodes > 1
                    else 0.0
                )

        # Unsafe action selection rates (distance-based)
        if 'unsafe_frames' in df.columns:
            unsafe_frames = float(df['unsafe_frames'].sum())
            unsafe_cols = [c for c in df.columns if c.startswith('unsafe_') and c.endswith('_count')
                           and not c.startswith('unsafe_ttc_')]
            if unsafe_frames > 0:
                for col in unsafe_cols:
                    base = col[len('unsafe_') : -len('_count')]
                    rate_col = f'unsafe_{base}_rate'
                    total_cnt = float(df[col].sum())
                    out[rate_col] = total_cnt / unsafe_frames

        # Unsafe action selection rates (TTC-based)
        if 'unsafe_ttc_frames' in df.columns:
            unsafe_ttc_frames = float(df['unsafe_ttc_frames'].sum())
            unsafe_ttc_cols = [c for c in df.columns
                               if c.startswith('unsafe_ttc_') and c.endswith('_count')]
            if unsafe_ttc_frames > 0:
                for col in unsafe_ttc_cols:
                    base = col[len('unsafe_ttc_') : -len('_count')]
                    rate_col = f'unsafe_ttc_{base}_rate'
                    total_cnt = float(df[col].sum())
                    out[rate_col] = total_cnt / unsafe_ttc_frames

        # Supervisor statistics: average convergence metrics, outcome fractions
        if 'mean_iterations_to_converge' in df.columns:
            out['mean_iterations_to_converge'] = float(df['mean_iterations_to_converge'].mean())
        if 'convergence_rate' in df.columns:
            out['convergence_rate'] = float(df['convergence_rate'].mean())

        outcome_cols = [c for c in df.columns
                        if c.startswith('outcome_') and c.endswith('_count')]
        if outcome_cols:
            total_outcomes = float(df[outcome_cols].to_numpy().sum())
            for col in outcome_cols:
                frac_col = col[: -len('_count')] + '_fraction'
                out[frac_col] = (
                    float(df[col].sum()) / total_outcomes if total_outcomes > 0 else 0.0
                )

        # Return as single-row DataFrame for compatibility
        return pd.DataFrame([out])
    for filename in csv_files:
        config = parse_configuration_from_filename(filename, results_dir=results_dir)
        if config is None:
            print(f"Warning: Could not parse configuration from filename: {filename}")
            continue
        filepath = os.path.join(results_dir, filename)
        try:
            df = pd.read_csv(filepath)
            if df.empty:
                continue

            # All result files are stored with per-episode rows; aggregate to a
            # single per-experiment row for downstream analysis.
            df_processed = _aggregate_episode_level_df(df)

            # Alias RCPS→SCPS outcome column for details tables.
            if (
                "outcome_rcps_augmented_fraction" in df_processed.columns
                and "outcome_scps_augmented_fraction" not in df_processed.columns
            ):
                df_processed["outcome_scps_augmented_fraction"] = df_processed[
                    "outcome_rcps_augmented_fraction"
                ]

            for key, value in config.items():
                df_processed[key] = value
            grouped_data[tuple(sorted(config.items()))].append(df_processed)
        except Exception as e:
            print(f"Warning: Could not read {filename}: {e}")
    return grouped_data


def calculate_statistics(group_data):
    """Calculate mean and standard deviation for all numeric columns.
    
    :param group_data: List of DataFrames for a configuration group.
    :return: Tuple of (stats dictionary, number of experiments).
    """
    combined_df = pd.concat(group_data, ignore_index=True)
    config_cols = ['profile', 'method', 'value', 'model', 'env', 'mode', 'filter']
    numeric_cols = [col for col in combined_df.columns 
                   if col not in config_cols and combined_df[col].dtype in ['float64', 'int64']]
    stats = {}
    for col in numeric_cols:
        values = combined_df[col].dropna()
        if len(values) > 0:
            mean_val = values.mean()
            std_val = values.std()
            stats[col] = (mean_val, std_val)
        else:
            stats[col] = (np.nan, np.nan)

    # Override selected metrics to use pooled std over episodes (rather than across experiments)
    pooled_specs = [
        ("mean_total_reward", "std_total_reward_episodes"),
        ("mean_basic_reward", "std_basic_reward_episodes"),
        ("mean_total_cost", "std_total_cost_episodes"),
        ("mean_added_reward", "std_added_reward_episodes"),
        ("mean_normalized_lane_index", "std_normalized_lane_index_episodes"),
        ("mean_total_expected_cost", "std_total_expected_cost_episodes"),
        ("mean_courtesy_gap_violation", "std_courtesy_gap_violation_episodes"),
    ]
    for mean_col, std_col in pooled_specs:
        if mean_col in combined_df.columns and std_col in combined_df.columns and "num_episodes" in combined_df.columns:
            means = combined_df[mean_col].to_numpy()
            stds = combined_df[std_col].to_numpy()
            counts = combined_df["num_episodes"].to_numpy()

            mask = (~np.isnan(means)) & (~np.isnan(stds)) & (~np.isnan(counts)) & (counts > 0)
            if not np.any(mask):
                continue
            means = means[mask]
            stds = stds[mask]
            counts = counts[mask]

            N = counts.sum()
            if N <= 1:
                # Not enough total episodes; fall back to default stats
                continue

            # Pooled mean over episodes
            pooled_mean = float((counts * means).sum() / N)

            # Pooled variance over episodes:
            # sum_j [ (n_j - 1)*s_j^2 + n_j*(μ_j - μ)^2 ] / (N - 1)
            sq_terms = (counts - 1) * (stds ** 2) + counts * (means - pooled_mean) ** 2
            pooled_var = float(sq_terms.sum() / (N - 1))
            pooled_std = float(np.sqrt(pooled_var)) if pooled_var >= 0 else 0.0

            stats[mean_col] = (pooled_mean, pooled_std)

    return stats, len(combined_df)


def format_statistic(mean_val, std_val, n_experiments, metric_name=None):
    """Format mean and episode-level standard deviation as ``mean ± std``.

    :param mean_val: mean value to format.
    :param std_val: sample standard deviation over episodes (``ddof=1``).
    :param n_experiments: unused; kept for call-site compatibility.
    :param metric_name: optional metric name for additional context.
    :return: formatted string, or ``"-"`` if no valid data.
    """
    del n_experiments, metric_name  # reserved for callers / future use
    if pd.isna(mean_val):
        return "-"
    if pd.isna(std_val):
        return f"{mean_val:.2f}"
    return f"{mean_val:.2f} ± {std_val:.2f}"


def format_collision_rate(group_data):
    """Format collision rate per hour.
    
    :param group_data: List of DataFrames for a configuration group.
    :return: Collision rate formatted as string.
    """
    total_distance = 0
    total_collisions = 0
    total_time_seconds = 0
    policy_period = 1  # TODO: Use environment config
    for df in group_data:
        if (
            'total_collisions' in df.columns
            and 'mean_speed' in df.columns
            and 'mean_episode_length' in df.columns
            and 'num_episodes' in df.columns
        ):
            for idx, row in df.iterrows():
                collisions = row.get('total_collisions', 0)
                speed = row.get('mean_speed', np.nan)
                ep_length = row.get('mean_episode_length', np.nan)
                num_episodes = row.get('num_episodes', np.nan)
                if not np.isnan(speed) and not np.isnan(ep_length) and not np.isnan(num_episodes):
                    distance = speed * ep_length * policy_period * num_episodes
                    total_distance += distance
                    total_collisions += collisions
                    total_time_seconds += ep_length * policy_period * num_episodes
    if total_collisions == 0:
        return "0.00"
    else:
        total_time_hours = total_time_seconds / 3600
        collision_rate = total_collisions / total_time_hours
        # Episode-level Bernoulli collision indicator has std sqrt(p*(1-p)).
        # Propagate that std (not SE) to the hourly collision rate.
        n = sum([df['num_episodes'].sum() for df in group_data])
        p = total_collisions / n if n > 0 else 0.0
        std_p = np.sqrt(p * (1 - p)) if n > 1 else 0.0
        mean_episode_length = total_time_seconds / n if n > 0 else 1
        std_collision_rate = (3600 * std_p) / (mean_episode_length * policy_period)
        return f"{collision_rate:.2f} ± {std_collision_rate:.2f}"


def compute_success_rate(group_data):
    """Compute success rate as percentage of episodes without collision.
    
    :param group_data: List of DataFrames for a configuration group.
    :return: Success rate as a percentage string.
    """
    total_collisions = 0
    total_episodes = 0
    for df in group_data:
        if 'total_collisions' in df.columns and 'num_episodes' in df.columns:
            total_collisions += df['total_collisions'].sum()
            total_episodes += df['num_episodes'].sum()
    if total_episodes == 0:
        return "-"
    success_rate = 100 * (total_episodes - total_collisions) / total_episodes
    return f"{success_rate:.2f}"


def create_config_name(config_dict):
    """Return a concise label for a configuration.
    
    :param config_dict: Configuration dictionary.
    :return: Concise label string.
    """
    method = config_dict.get('method', '')
    value = config_dict.get('value')
    filter_status = config_dict.get('filter')

    base = method.title()
    if method.lower() in {'adaptive', 'fixed'} and value is not None:
        base = f"{base} ({value:g})"

    if filter_status in {'filtered', 'unfiltered'}:
        suffix = 'Filtered' if filter_status == 'filtered' else 'Unfiltered'
        return f"{base} [{suffix}]"
    return base


def method_sort_key(config):
    """Sort key for methods.
    
    :param config: Configuration dictionary.
    :return: Tuple used for sorting methods.
    """
    method = config.get('method', '').lower()
    value = config.get('value', 0)
    filter_status = config.get('filter')
    # Unfiltered (or unspecified) first, then filtered
    filter_ord = 0 if filter_status in (None, 'unfiltered') else 1
    if method == 'unsupervised':
        return (0, filter_ord, 0)
    elif method == 'filter_only':
        return (1, filter_ord, 0)
    elif method == 'naive':
        return (2, filter_ord, 0)
    elif method == 'adaptive':
        return (3, filter_ord, float(value) if value is not None else 0)
    elif method == 'fixed':
        return (4, filter_ord, float(value) if value is not None else 0)
    else:
        return (99, filter_ord, 0)


def generate_markdown_tables(grouped_data):
    """Generate markdown tables from grouped data, one per model-environment combination.
    
    :param grouped_data: Dictionary mapping configuration tuples to lists of DataFrames.
    :return: Tuple of (summary_tables, details_tables).
    """
    
    # Include mean_courtesy_gap_violation only when present in any loaded result.
    has_courtesy_gap_violation = any(
        'mean_courtesy_gap_violation' in df.columns
        for group_data in grouped_data.values()
        for df in group_data
    )

    core_metrics = [
        'mean_total_reward',
        'mean_basic_reward',
        'mean_added_reward',
        'mean_total_cost',
        'mean_total_expected_cost',
        'mean_normalized_lane_index',
    ]
    if has_courtesy_gap_violation:
        core_metrics.append('mean_courtesy_gap_violation')

    summary_metric_categories = {
        # For the top-of-summary tables, focus on reward decomposition
        # (mean reward per episode, not rates), realised/expected norm cost,
        # and the average normalised lane index.
        'Core Metrics': core_metrics
    }

    details_metric_categories = {
        'Supervisor Statistics': [
            'mean_iterations_to_converge', 'convergence_rate',
            'outcome_unchanged_fraction', 'outcome_naively_augmented_fraction',
            'outcome_scps_augmented_fraction', 'outcome_projection_fraction'
        ]
    }
    
    display_names = {
        # Summary metrics
        'mean_episode_length'    : 'Episode Length',
        'collision_rate'         : 'Collision Rate',
        'mean_speed'                 : 'Speed',
        'cost_rate'                  : 'Cost Rate',
        'mean_total_cost'            : 'Total Norm Cost',
        'mean_total_expected_cost'   : 'Expected Norm Cost',
        'mean_normalized_lane_index' : 'Normalised Lane Index',
        'mean_courtesy_gap_violation': 'Mean Courtesy Gap Violation (full ep.)',
        'avoided_cost_rate'      : 'Avoided Cost Rate',
        'mean_total_reward'      : 'Total Reward',
        'mean_basic_reward'      : 'Basic Reward',
        'mean_added_reward'      : 'Added Reward',
        
        # Supervisor statistics (details.md)
        'mean_iterations_to_converge'             : 'Mean Iterations to Converge',
        'convergence_rate'                        : 'Convergence Rate',
        'outcome_unchanged_fraction'              : 'Unchanged Fraction',
        'outcome_naively_augmented_fraction'      : 'Naively Augmented Fraction',
        'outcome_scps_augmented_fraction'         : 'SCPS Augmented Fraction',
        'outcome_projection_fraction'             : 'Projection Fraction',
    }
    # Build header rows
    summary_header_cols = ['Method']
    for category, metrics in summary_metric_categories.items():
        for metric in metrics:
            col_name = display_names.get(metric, metric)
            summary_header_cols.append(col_name)

    details_header_cols = ['Method']
    for category, metrics in details_metric_categories.items():
        for metric in metrics:
            col_name = display_names.get(metric, metric)
            details_header_cols.append(col_name)
    
    # Group data by model-environment combination first, then by profile
    model_env_groups = defaultdict(lambda: defaultdict(dict))
    for config_tuple, group_data in grouped_data.items():
        config_dict = dict(config_tuple)
        model_env_key = (config_dict['model'], config_dict['env'])
        profile = config_dict['profile']
        model_env_groups[model_env_key][profile][config_tuple] = group_data
    
    summary_tables = []
    details_tables = []
    
    for (model, env), profile_configs in sorted(model_env_groups.items()):
        # Build table rows for this model-environment combination
        summary_rows = []
        summary_configs = []
        details_rows = []
        
        for profile, configs in sorted(profile_configs.items()):
            # Add separator row if not the first profile
            if summary_rows:
                summary_rows.append([''] * len(summary_header_cols))
                summary_configs.append(None)
                details_rows.append([''] * len(details_header_cols))
            
            # Add section header
            section_header = f"**{profile.title()} Profile**"
            summary_separator_row = [section_header] + [''] * (len(summary_header_cols) - 1)
            details_separator_row = [section_header] + [''] * (len(details_header_cols) - 1)
            summary_rows.append(summary_separator_row)
            summary_configs.append(None)
            details_rows.append(details_separator_row)
            
            # Sort configs by method_sort_key
            sorted_configs = sorted(configs.items(), key=lambda item: method_sort_key(dict(item[0])))
            
            for config_tuple, group_data in sorted_configs:
                config_dict = dict(config_tuple)
                stats, n_experiments = calculate_statistics(group_data)
                config_name = create_config_name(config_dict)

                # Build summary data row
                summary_row = [config_name]
                for category, metrics in summary_metric_categories.items():
                    for metric in metrics:
                        if metric == 'collision_rate':
                            # Keep existing collision-rate formatting (per hour)
                            summary_row.append(format_collision_rate(group_data))
                        elif metric in stats:
                            mean_val, std_val = stats[metric]
                            # For all other metrics, report raw means/stds (no per-hour scaling)
                            summary_row.append(format_statistic(mean_val, std_val, n_experiments, metric))
                        else:
                            summary_row.append("-")
                summary_rows.append(summary_row)
                summary_configs.append(config_dict)
                
                # Build details data row
                details_row = [config_name]
                for category, metrics in details_metric_categories.items():
                    for metric in metrics:
                        if metric in stats:
                            mean_val, std_val = stats[metric]
                            # Report raw means/stds for all metrics (no per-hour conversion)
                            details_row.append(format_statistic(mean_val, std_val, n_experiments, metric))
                        else:
                            details_row.append("-")
                details_rows.append(details_row)
        
        summary_tables.append({
            'model': model,
            'env': env,
            'header_cols': summary_header_cols,
            'rows': summary_rows,
            'configs': summary_configs
        })
        details_tables.append({
            'model': model,
            'env': env,
            'header_cols': details_header_cols,
            'rows': details_rows,
            'configs': summary_configs
        })
    
    return summary_tables, details_tables


def generate_summary_table(grouped_data):
    """Generate a summary table for each configuration.
    
    The main summary focuses on success rate and reward-based metrics:
    - Success rate (% of episodes without collision)
    - Mean total reward (aggregated across experiments)
    - Mean basic reward
    - Mean added reward
    """
    summary_rows = []
    seen_keys = set()
    
    # Collect all unique configurations
    all_configs = []
    for config_tuple, group_data in grouped_data.items():
        config_dict = dict(config_tuple)
        key = (
            config_dict['profile'],
            config_dict['model'],
            config_dict['env'],
            config_dict['method'],
            config_dict['value'],
            config_dict.get('filter'),
        )
        if key in seen_keys:
            continue
        seen_keys.add(key)
        # With filter status removed, treat all configurations as main results.
        all_configs.append(config_dict)
    
    # Sort configurations
    all_configs.sort(key=lambda x: (x['profile'], x['model'], x['env'], x['method'], x.get('filter') or '', x['value'] or 0))
    
    for config in all_configs:
        config_tuple = tuple(sorted(config.items()))
        if config_tuple in grouped_data:
            group_data = grouped_data[config_tuple]
            stats, n_experiments = calculate_statistics(group_data)

            # Success rate (% of episodes without collision)
            success_rate = compute_success_rate(group_data)
            method_name = create_config_name(config)

            # Reward-based metrics: use aggregated per-episode means/stds directly
            def _format_rate(metric_name):
                if metric_name not in stats:
                    return "-"
                mean_val, std_val = stats[metric_name]
                return format_statistic(mean_val, std_val, n_experiments, metric_name)

            total_reward_str = _format_rate('mean_total_reward')
            basic_reward_str = _format_rate('mean_basic_reward')
            added_reward_str = _format_rate('mean_added_reward')

            # Create row: Profile, Model-Env, Method, Success Rate, Reward, Basic, Added
            row = [
                config['profile'].title(),
                f"{config['model']} {config['env']}",
                method_name,
                success_rate,
                total_reward_str,
                basic_reward_str,
                added_reward_str,
            ]
            summary_rows.append(row)
    
    # Reverse the order so most interesting results appear at the top
    return summary_rows[::-1]


def write_table_section(f, title, header_cols, rows):
    """Write a table section to the file."""
    f.write(f"\n### {title}\n\n")
    f.write("| " + " | ".join(header_cols) + " |\n")
    f.write("|" + "|".join(["---"] * len(header_cols)) + "|\n")
    for row in rows:
        f.write("| " + " | ".join(str(cell) for cell in row) + " |\n")


def _episode_count(group_data) -> int:
    """Total number of episodes across all experiments in ``group_data``."""
    total = 0
    for df in group_data:
        if 'num_episodes' in df.columns:
            total += int(df['num_episodes'].sum())
    return total


def _ci95_halfwidth(std_val, n: int) -> float:
    """Half-width of a normal-approx 95% CI: ``1.96 * std / sqrt(n)``."""
    if n <= 1 or pd.isna(std_val):
        return 0.0
    return float(1.96 * float(std_val) / np.sqrt(n))


def generate_adaptive_trend_plot(
    grouped_data,
    output_dir,
    adaptive_values,
    title=None,
):
    """Generate KL-budget sweep: original reward (top) and norm cost (bottom).

    Prefer filtered adaptive runs when both filtered and unfiltered exist for
    the same ``\\delta`` value. Error bands are normal-approx 95% CIs
    (``1.96 * std / sqrt(n_episodes)``). Filtered cost-optimal projection
    means are drawn as horizontal dashed target lines when available.
    """
    del title  # retained for call-site compatibility; adaptive plots are untitled
    plots_dir = os.path.join(output_dir, 'plots')
    os.makedirs(plots_dir, exist_ok=True)

    # Group adaptive sweeps by model-env-profile-value, preferring filtered
    # over unfiltered. Also retain reference baselines:
    # - filtered projection (cost-optimal target)
    # - nop unfiltered (unshaped base policy)
    model_env_profile_groups = defaultdict(lambda: defaultdict(dict))
    filtered_projection_groups = defaultdict(dict)
    nop_unfiltered_groups = defaultdict(dict)
    for config_tuple, group_data in grouped_data.items():
        config_dict = dict(config_tuple)
        model_env_key = (config_dict['model'], config_dict['env'])
        profile = config_dict['profile']

        if (
            config_dict['method'] == 'projection'
            and config_dict.get('filter') == 'filtered'
        ):
            filtered_projection_groups[model_env_key][profile] = group_data
            continue

        if (
            config_dict['method'] == 'nop'
            and config_dict.get('filter') == 'unfiltered'
        ):
            nop_unfiltered_groups[model_env_key][profile] = group_data
            continue

        if config_dict['method'] != 'adaptive':
            continue

        value = config_dict.get('value')
        if value is None or value not in adaptive_values:
            continue

        is_filtered = config_dict.get('filter') == 'filtered'
        existing = model_env_profile_groups[model_env_key][profile].get(value)
        if existing is None:
            model_env_profile_groups[model_env_key][profile][value] = {
                'group_data': group_data,
                'filtered': is_filtered,
            }
        elif is_filtered and not existing['filtered']:
            model_env_profile_groups[model_env_key][profile][value] = {
                'group_data': group_data,
                'filtered': True,
            }

    for (model, env), profile_map in sorted(model_env_profile_groups.items()):
        for profile, value_map in sorted(profile_map.items()):
            if not value_map:
                continue

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(3.25, 3.6), sharex=True)

            LABEL_FONTSIZE = 9
            LEGEND_FONTSIZE = 8
            TICK_FONTSIZE = 8
            MARKER_SIZE = 4.0
            ERRORBAR_LINEWIDTH = 1.2

            x_vals = []
            y_reward = []
            y_reward_err = []
            y_cost = []
            y_cost_err = []

            for value in sorted(adaptive_values):
                if value not in value_map:
                    continue
                group_data = value_map[value]['group_data']
                stats, _n_experiments = calculate_statistics(group_data)

                if 'mean_basic_reward' not in stats or 'mean_total_cost' not in stats:
                    continue
                reward_mean, reward_std = stats['mean_basic_reward']
                cost_mean, cost_std = stats['mean_total_cost']
                if pd.isna(reward_mean) or pd.isna(cost_mean):
                    continue

                n_eps = _episode_count(group_data)
                x_vals.append(value)
                y_reward.append(float(reward_mean))
                y_reward_err.append(_ci95_halfwidth(reward_std, n_eps))
                y_cost.append(float(cost_mean))
                y_cost_err.append(_ci95_halfwidth(cost_std, n_eps))

            if not x_vals:
                plt.close(fig)
                continue

            x_arr = np.asarray(x_vals, dtype=float)
            reward_arr = np.asarray(y_reward, dtype=float)
            reward_err_arr = np.asarray(y_reward_err, dtype=float)
            cost_arr = np.asarray(y_cost, dtype=float)
            cost_err_arr = np.asarray(y_cost_err, dtype=float)

            LINE_COLOR = '#1F4E79'
            PROJECTION_COLOR = '#666666'
            NOP_COLOR = '#666666'

            ax1.fill_between(
                x_arr, reward_arr - reward_err_arr, reward_arr + reward_err_arr,
                color=LINE_COLOR, alpha=0.2, linewidth=0,
            )
            ax1.plot(
                x_arr, reward_arr,
                marker='o', color=LINE_COLOR, linestyle='-',
                linewidth=ERRORBAR_LINEWIDTH, markersize=MARKER_SIZE,
            )
            ax2.fill_between(
                x_arr, cost_arr - cost_err_arr, cost_arr + cost_err_arr,
                color=LINE_COLOR, alpha=0.2, linewidth=0,
            )
            ax2.plot(
                x_arr, cost_arr,
                marker='o', color=LINE_COLOR, linestyle='-',
                linewidth=ERRORBAR_LINEWIDTH, markersize=MARKER_SIZE,
                label='Adaptive-$\\beta$\nSCPS',
            )

            def _draw_reference_lines(group_data, color, linestyle, label):
                """Draw reward/cost horizontal references; label only on bottom axis."""
                target_stats, _ = calculate_statistics(group_data)
                target_reward = target_stats.get('mean_basic_reward', (np.nan, np.nan))[0]
                target_cost = target_stats.get('mean_total_cost', (np.nan, np.nan))[0]
                if pd.isna(target_reward) or pd.isna(target_cost):
                    return None
                ax1.axhline(
                    y=float(target_reward),
                    color=color,
                    linestyle=linestyle,
                    linewidth=1.5,
                )
                ax2.axhline(
                    y=float(target_cost),
                    color=color,
                    linestyle=linestyle,
                    linewidth=1.5,
                    label=label,
                )
                return float(target_reward), float(target_cost)

            has_reference_lines = False
            nop_target = nop_unfiltered_groups.get((model, env), {}).get(profile)
            if nop_target is not None:
                targets = _draw_reference_lines(
                    nop_target,
                    NOP_COLOR,
                    '--',
                    'RL Prior',
                )
                if targets is not None:
                    has_reference_lines = True
                    print(
                        f"NOP unfiltered targets for {env}/{profile}: "
                        f"reward={targets[0]:.3f}, cost={targets[1]:.3f}"
                    )

            projection_target = filtered_projection_groups.get((model, env), {}).get(profile)
            if projection_target is not None:
                targets = _draw_reference_lines(
                    projection_target,
                    PROJECTION_COLOR,
                    '-.',
                    'Cost-optimal\nProjection',
                )
                if targets is not None:
                    has_reference_lines = True
                    print(
                        f"Filtered projection targets for {env}/{profile}: "
                        f"reward={targets[0]:.3f}, cost={targets[1]:.3f}"
                    )

            if max(adaptive_values) / min(adaptive_values) > 10:
                ax1.set_xscale('log')
                ax2.set_xscale('log')

            ax1.grid(True, alpha=0.3)
            ax2.grid(True, alpha=0.3)

            ax1.set_ylabel(r"Original Reward", fontsize=LABEL_FONTSIZE)
            ax2.set_ylabel(r"Norm-violation Cost", fontsize=LABEL_FONTSIZE)
            ax2.set_xlabel(r"KL Budget $\left(\delta\right)$", fontsize=LABEL_FONTSIZE)
            for ax in (ax1, ax2):
                ax.tick_params(axis='both', which='major', labelsize=TICK_FONTSIZE)
                ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.1f'))

            plt.tight_layout()
            fig.align_ylabels([ax1, ax2])
            if has_reference_lines:
                handles, labels = ax2.get_legend_handles_labels()
                legend_order = {
                    'RL Prior': 0,
                    'Adaptive-$\\beta$\nSCPS': 1,
                    'Cost-optimal\nProjection': 2,
                }
                handles, labels = zip(*sorted(
                    zip(handles, labels),
                    key=lambda item: legend_order[item[1]],
                ))
                ax2.legend(
                    handles,
                    labels,
                    loc='center right',
                    fontsize=LEGEND_FONTSIZE,
                )

            profile_slug = str(profile).replace(' ', '_')
            plot_file = os.path.join(
                plots_dir, f'adaptive_trends_{model}_{env}_{profile_slug}.pdf'
            )
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            png_file = plot_file.replace('.pdf', '.png')
            plt.savefig(png_file, dpi=200, bbox_inches='tight')
            plt.close()
            print(f"Adaptive trends plot saved to: {plot_file}")
            print(f"Adaptive trends preview saved to: {png_file}")

def generate_clustered_bar_plot(
    grouped_data,
    output_dir,
    selected_value=1.00,
    prefix="unsafe_ttc_",
    suffix="_rate",
    exclude_prefixes=None,
    desired_order=None,
    display_map=None,
    y_label="Rate",
    plot_title=None,
):
    """Generate clustered bar charts for unsafe-event action selection rates.

    Parameters
    ----------
    grouped_data : dict
        Mapping of configuration tuples to lists of pandas DataFrames (same as elsewhere).
    output_dir : str
        Directory where `plots/` subfolder will be created (if not present).
    selected_value : float, optional
        delta value to pick for the adaptive beta experiments (default 1.0).
    prefix : str, optional
        Column-name prefix (e.g., ``"unsafe_"`` or ``"unsafe_ttc_"``).
    suffix : str, optional
        Column-name suffix (e.g., ``"_rate"`` or ``"_preference"``).
    exclude_prefixes : list of str, optional
        List of prefixes to exclude from action columns (e.g., ``["unsafe_ttc_"]`` for distance plots).
    desired_order : list of str, optional
        Explicit category ordering. If provided, categories appear in this order (followed by any remaining categories sorted).
    display_map : dict, optional
        Mapping from raw category key to label for x-tick. If omitted, auto-generated labels are used.
    y_label : str, optional
        Label for the y-axis.
    plot_title : str, optional
        If provided, override the automatic title.
    """

    from collections import defaultdict

    # --------------------------- Plot style constants --------------------------- #
    FIGSIZE = (3.25, 2.6)
    BAR_WIDTH = 0.25
    CAPS_SIZE = 3
    LABEL_FONTSIZE = 9
    TICK_FONTSIZE = 8
    LEGEND_FONTSIZE = 7
    TITLE_FONTSIZE = 10

    plots_dir = os.path.join(output_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    # Organise data we care about
    groups_by_model_env = defaultdict(lambda: {
        "unsupervised": [],
        "cautious_adaptive": [],
        "efficient_adaptive": [],
    })

    for config_tuple, group_data in grouped_data.items():
        cfg = dict(config_tuple)
        key = (cfg["model"], cfg["env"])

        # Only consider filtered configurations for supervised runs; use unfiltered/unspecified
        # for the unsupervised baseline.
        filter_status = cfg.get("filter")

        # Unsupervised baseline (profile agnostic)
        if cfg.get("method") == "unsupervised" and filter_status in (None, "unfiltered"):
            groups_by_model_env[key]["unsupervised"].extend(group_data)

        # Adaptive beta (delta = selected_value), filtered runs only
        elif (
            cfg.get("method") == "adaptive"
            and abs(float(cfg.get("value", 0)) - float(selected_value)) < 1e-6
            and filter_status == "filtered"
        ):
            if cfg.get("profile") == "cautious":
                groups_by_model_env[key]["cautious_adaptive"].extend(group_data)
            elif cfg.get("profile") == "efficient":
                groups_by_model_env[key]["efficient_adaptive"].extend(group_data)

    # Helper to compute mean & sample std for a single column across a list of dfs
    def _mean_std(dfs, col):
        import numpy as np
        import pandas as pd

        if not dfs:
            return np.nan, 0.0
        vals = []
        for df in dfs:
            if col in df.columns:
                vals.append(df[col])
        if not vals:
            return np.nan, 0.0
        series = pd.concat(vals).dropna()
        if series.empty:
            return np.nan, 0.0
        mean = series.mean()
        std = float(series.std(ddof=1)) if len(series) > 1 else 0.0
        return mean, std

    # Iterate through model–env combos and draw plots
    ACTION_PREFIX = prefix
    EXCLUDE_PREFIXES = set(exclude_prefixes or [])
    ACTION_SUFFIX = suffix

    for (model, env), data_dict in sorted(groups_by_model_env.items()):
        if not all(data_dict.values()):
            # Skip combos where we do not have all three experimental groups
            continue

        # Derive list of actions from any dataframe we have
        action_cols = set()
        for dfs in data_dict.values():
            for df in dfs:
                for c in df.columns:
                    if not c.endswith(ACTION_SUFFIX):
                        continue
                    if not c.startswith(ACTION_PREFIX):
                        continue
                    if any(c.startswith(ex) for ex in EXCLUDE_PREFIXES):
                        continue
                    action_cols.add(c)
        # Avoid empty action list after filtering
        if not action_cols:
            continue

        raw_categories = [
            col[len(ACTION_PREFIX) : -len(ACTION_SUFFIX)] for col in action_cols
        ]
        if desired_order is not None:
            categories = [c for c in desired_order if c in raw_categories] + [
                c for c in sorted(raw_categories) if c not in desired_order
            ]
        else:
            categories = sorted(raw_categories)

        # Collect statistics (mean ± sample std over episodes)
        stats = {key: {"means": [], "ses": []} for key in data_dict.keys()}
        for cat in categories:
            col_name = f"{ACTION_PREFIX}{cat}{ACTION_SUFFIX}"
            for key in stats.keys():
                mean, std = _mean_std(data_dict[key], col_name)
                stats[key]["means"].append(mean)
                stats[key]["ses"].append(std)

        # Plot
        import numpy as np
        import matplotlib.pyplot as plt

        ind = np.arange(len(categories))
        width = BAR_WIDTH
        fig, ax = plt.subplots(figsize=FIGSIZE)

        ax.bar(
            ind - width,
            stats["unsupervised"]["means"],
            width,
            yerr=stats["unsupervised"]["ses"],
            label="Unsupervised",
            color=colors['gray'],
            capsize=CAPS_SIZE,
        )
        ax.bar(
            ind,
            stats["cautious_adaptive"]["means"],
            width,
            yerr=stats["cautious_adaptive"]["ses"],
            label=r"Cautious",
            color=colors['teal'],
            capsize=CAPS_SIZE,
        )
        ax.bar(
            ind + width,
            stats["efficient_adaptive"]["means"],
            width,
            yerr=stats["efficient_adaptive"]["ses"],
            label=r"Efficient",
            color=colors['purple'],
            capsize=CAPS_SIZE,
        )

        ax.set_xticks(ind)
        if display_map is None:
            default_map = {
                "faster": "Faster",
                "slow": "Slower",
                "idle": "Idle",
                "lane": "Lane Change",
            }
            effective_map = default_map
        else:
            effective_map = display_map
        ax.set_xticklabels([
            effective_map.get(c, c.replace("_", " ").title()) for c in categories
        ], fontsize=TICK_FONTSIZE)
        ax.set_ylabel(y_label, fontsize=LABEL_FONTSIZE)
        ax.set_xlabel("Action", fontsize=LABEL_FONTSIZE)
        ax.legend(fontsize=LEGEND_FONTSIZE)
        # Title handling
        if plot_title is None:
            plot_title = "Clustered Bar Plot"
        ax.set_title(plot_title, fontsize=TITLE_FONTSIZE)
        ax.grid(True, axis="y", alpha=0.3)
        plt.tight_layout()

        plot_kind = "unsafe_ttc" if prefix == "unsafe_ttc_" else ("unsafe_distance" if prefix.startswith("unsafe_") else "lane_occ")
        plot_file = os.path.join(plots_dir, f"{plot_kind}_bar_{model}_{env}.pdf")
        plt.savefig(plot_file, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Bar plot saved to: {plot_file}")

def generate_lane_occupancy_stacked_bar_plot(grouped_data, output_dir, selected_value=1.00):
    """Generate stacked bar charts of lane occupancy distribution.

    One bar per profile (Unsupervised, Cautious, Efficient) with segments
    representing mean occupancy for each lane. Colors encode lane indices.
    """

    from collections import defaultdict
    import numpy as np
    import matplotlib.pyplot as plt

    FIGSIZE = (3.25, 2.6)
    TITLE_FONTSIZE = 10
    LABEL_FONTSIZE = 9
    LEGEND_FONTSIZE = 7
    BAR_HEIGHT = 0.8

    plots_dir = os.path.join(output_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    groups_by_model_env = defaultdict(lambda: {
        "unsupervised": [],
        "cautious_adaptive": [],
        "efficient_adaptive": [],
    })

    for cfg_tuple, gdata in grouped_data.items():
        cfg = dict(cfg_tuple)
        key = (cfg["model"], cfg["env"])
        filter_status = cfg.get("filter")

        if cfg.get("method") == "unsupervised" and filter_status in (None, "unfiltered"):
            groups_by_model_env[key]["unsupervised"].extend(gdata)
        elif (
            cfg.get("method") == "adaptive"
            and abs(float(cfg.get("value", 0)) - float(selected_value)) < 1e-6
            and filter_status == "filtered"
        ):
            if cfg.get("profile") == "cautious":
                groups_by_model_env[key]["cautious_adaptive"].extend(gdata)
            elif cfg.get("profile") == "efficient":
                groups_by_model_env[key]["efficient_adaptive"].extend(gdata)

    def _mean_per_lane(dfs):
        lane_cols = set()
        for df in dfs:
            lane_cols.update([c for c in df.columns if c.startswith("lane_") and c.endswith("_preference")])
        if not lane_cols:
            return None, 0
        idxs = sorted(int(c.split("_")[1]) for c in lane_cols)
        means = []
        for idx in idxs:
            col = f"lane_{idx}_preference"
            series_list = [df[col] for df in dfs if col in df.columns]
            if not series_list:
                means.append(np.nan)
            else:
                series = pd.concat(series_list).dropna()
                means.append(series.mean())
        return np.array(means), len(idxs)

    for (model, env), data_dict in sorted(groups_by_model_env.items()):
        if not all(data_dict.values()):
            continue

        unsup_means, n_lanes = _mean_per_lane(data_dict["unsupervised"])
        if unsup_means is None:
            continue
        cautious_means, _ = _mean_per_lane(data_dict["cautious_adaptive"])
        eff_means, _ = _mean_per_lane(data_dict["efficient_adaptive"])

        # Aggregate into Left (lanes 0..mid-1) and Right (mid..end) probabilities
        def _left_right(arr):
            if arr is None or len(arr) == 0:
                return np.array([np.nan, np.nan])
            mid = len(arr) // 2
            left = np.nansum(arr[:mid])
            right = np.nansum(arr[mid:])
            return np.array([left, right])

        unsup_lr = _left_right(unsup_means)
        cautious_lr = _left_right(cautious_means)
        eff_lr = _left_right(eff_means)

        data_matrix = np.vstack([unsup_lr, cautious_lr, eff_lr]).T  # shape (2, 3)
        n_categories = 2  # Left, Right

        # Shift bars down by 2 units to make room for legend at top
        y = np.array([1.8, 3.2, 4.6])  # unsupervised, cautious, efficient
        fig, ax = plt.subplots(figsize=FIGSIZE)

        lefts = np.zeros(3)
        # Generate purple shades from light (lane 1) to dark (lane n)
        legend_labels = ["Left Side of Road", "Right Side of Road"]

        for cat_idx in range(n_categories):
            vals = data_matrix[cat_idx]
            color = colors['medium_gray'] if cat_idx == 0 else colors['dark_gray']
            legend_label = legend_labels[cat_idx]
            ax.barh(
                y,
                vals,
                left=lefts,
                color=color,
                height=BAR_HEIGHT,
                label=legend_label,
            )
            lefts += vals

        # Adjust y-limits to include space at top for legend (add extra headroom)
        ax.set_ylim(y[-1] + 1.0, 0)  # inverted later

        # Remove default y tick labels
        ax.set_yticks([])

        # Add centered profile labels above each bar
        labels = ["Unsupervised", "Cautious", "Efficient"]
        for idx, lbl in enumerate(labels):
            y_pos = y[idx] - BAR_HEIGHT / 2 - 0.1
            ax.text(
                0.5,
                y_pos,
                lbl,
                ha="center",
                va="bottom",
                fontsize=LABEL_FONTSIZE,
            )

        ax.set_xlabel("Proportion of Time Spent in Lane Group", fontsize=LABEL_FONTSIZE, labelpad=6)
        ax.set_xlim(0, 1)
        # Natural y-axis orientation keeps Unsup at top
        n_cols = n_categories
        ax.legend(fontsize=LEGEND_FONTSIZE, ncol=n_cols, loc="upper center")
        
        ax.set_title("Lane Occupancy Across Behavior Profiles", fontsize=TITLE_FONTSIZE)

        plt.tight_layout()

        # No vertical lines needed after left/right aggregation

        plt.tight_layout()
        plot_file = os.path.join(plots_dir, f"lane_occ_stacked_{model}_{env}.pdf")
        plt.savefig(plot_file, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Lane-occupancy stacked bar plot saved to: {plot_file}")


def main():
    """Main function to analyze experiment results and generate tables and plots.
    
    Parses command line arguments, loads CSV result files, and generates markdown tables
    and visualization plots for the experiment results.
    """
    parser = argparse.ArgumentParser(description='Analyze experiment results from CSV files')
    parser.add_argument('--results-dir', required=True, 
                       help='Directory containing CSV result files')
    parser.add_argument('--output-dir', required=True,
                       help='Output directory for analysis files')
    parser.add_argument(
        '--fixed-values',
        default='',
        help=(
            'Comma-separated list of values to include for fixed method (e.g., 0.01,0.05,0.10). '
            'If omitted or empty, include all fixed-method runs.'
        ),
    )
    parser.add_argument(
        '--adaptive-values',
        default='',
        help=(
            'Comma-separated list of values to include for adaptive method (e.g., 0.01,0.05,0.10). '
            'If omitted or empty, include all adaptive-method runs.'
        ),
    )
    parser.add_argument('--plots', action='store_true',
                       help='Generate visualization plots (default: False)')
    parser.add_argument('--plot-adaptive-values', default='0.005,0.01,0.02,0.025,0.03,0.0316,0.05,0.3162,1.00,3.1623,10.000',
                       help='Comma-separated list of adaptive values to include in trend plots')
    
    
    args = parser.parse_args()
    
    # Parse allowed values for fixed and adaptive methods
    def parse_value_list(val):
        """Parse a comma-separated string of values into a list of floats.
        
        :param val: comma-separated string of numeric values.
        :return: list of float values, or None if input is empty or None.
        """
        if val is None or val.strip() == '':
            return None
        return [float(x) for x in val.split(',') if x.strip() != '']
    allowed_fixed_values = parse_value_list(args.fixed_values)
    allowed_adaptive_values = parse_value_list(args.adaptive_values)
    plot_adaptive_values = parse_value_list(args.plot_adaptive_values)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load and group data
    print(f"Scanning for CSV files in {args.results_dir}...")
    grouped_data = load_and_group_data(args.results_dir)
    
    if not grouped_data:
        print("No valid data found. Exiting.")
        return
    
    print(f"Found {len(grouped_data)} configuration groups")
    
    # Filter grouped_data based on allowed values
    def config_is_allowed(config):
        """Check if a configuration should be included based on allowed values.
        
        :param config: configuration dictionary containing method and value.
        :return: True if configuration should be included, False otherwise.
        """
        method = config.get('method', '')
        value = config.get('value', None)
        if method == 'fixed' and allowed_fixed_values is not None:
            return value in allowed_fixed_values
        if method == 'adaptive' and allowed_adaptive_values is not None:
            return value in allowed_adaptive_values
        return True  # All other methods always included
    
    filtered_grouped_data = {cfg: data for cfg, data in grouped_data.items() 
                           if config_is_allowed(dict(cfg))}
    
    # Generate markdown tables
    print("Generating markdown tables...")
    summary_tables, details_tables = generate_markdown_tables(filtered_grouped_data)
    
    # Generate summary table
    print("Generating summary table...")
    summary_rows = generate_summary_table(filtered_grouped_data)
    
    # Generate plots only if --plots flag is set
    if args.plots:
        # Publication plots historically used LaTeX; fall back to mathtext when
        # the local TeX install is incomplete (common on WSL / Colab images).
        plt.rcParams.update({
            "text.usetex": False,
            "mathtext.fontset": "cm",
            "font.family": "serif",
        })
        # Generate adaptive trends plot
        if plot_adaptive_values:
            print("Generating adaptive trends plot...")
            generate_adaptive_trend_plot(
                grouped_data=grouped_data,
                output_dir=args.output_dir,
                adaptive_values=plot_adaptive_values,
            )
        
        # Generate clustered-bar plots for unsafe TTC and unsafe distance
        print("Generating unsafe TTC bar plot...")
        generate_clustered_bar_plot(
            grouped_data,
            args.output_dir,
            selected_value=0.10,
            prefix="unsafe_ttc_",
            y_label="Action Selection Rate",
            plot_title="Action Selection Across Behavior Profiles\nDuring $\mathrm{TTC} < 3~\mathrm{s}$ Exposure",
            desired_order=["faster", "idle", "slow", "lane"],
        )

        print("Generating unsafe distance bar plot...")
        generate_clustered_bar_plot(
            grouped_data,
            args.output_dir,
            selected_value=0.10,
            prefix="unsafe_",
            exclude_prefixes=["unsafe_ttc_"],
            y_label="Action Selection Rate",
            plot_title="Action Selection Across Behavior Profiles\nDuring $d < 3L$ Exposure",
            desired_order=["faster", "idle", "slow", "lane"],
        )

        # Generate stacked bar plot for lane occupancy
        print("Generating lane-occupancy stacked bar plot...")
        generate_lane_occupancy_stacked_bar_plot(grouped_data, args.output_dir, selected_value=0.10)
    
    # Write summary.md
    summary_file = os.path.join(args.output_dir, 'summary.md')
    with open(summary_file, 'w') as f:
        f.write("# Experiment Results Summary\n")
    
    # Write each summary table
    for table_data in summary_tables:
        model = table_data['model']
        env = table_data['env']
        header_cols = table_data['header_cols']
        rows = table_data['rows']
        configs = table_data.get('configs', [None] * len(rows))
        try:
            collision_idx = header_cols.index('Collision Rate (hr^-1)')
        except ValueError:
            collision_idx = 1
        
        extended_header_cols = header_cols[:collision_idx] + ['Success Rate (%)'] + header_cols[collision_idx:]
        
        # Build main rows and success rates; keep filtered and unfiltered configurations separate.
        main_rows = []
        seen_main_methods = set()

        for row, config in zip(rows, configs):
            if config is None:
                main_rows.append(row[:collision_idx] + [''] + row[collision_idx:])
                continue

            method_key = (
                config['profile'],
                config['method'],
                config.get('value', None),
                config.get('filter', None),
            )
            config_tuple = tuple(sorted(config.items()))
            group_data = filtered_grouped_data.get(config_tuple, None)
            success_rate = compute_success_rate(group_data) if group_data is not None else "-"
            new_row = row[:collision_idx] + [success_rate] + row[collision_idx:]

            if method_key not in seen_main_methods:
                main_rows.append(new_row)
                seen_main_methods.add(method_key)
        
        with open(summary_file, 'a') as f:
            f.write(f"\n## {model} {env} Results\n\n")
            write_table_section(f, "Main Experimental Results", extended_header_cols, main_rows)
    
    # Write summary table (main summary: number of episodes per experiment)
    with open(summary_file, 'a') as f:
        f.write("\n## Experiment Summary\n\n")
        f.write("| Profile | Model-Environment | Method | Experiments | Total Episodes |\n")
        f.write("|---------|-------------------|--------|-------------|----------------|\n")

        # Reconstruct the set of configurations (same criteria as in generate_summary_table)
        seen_keys = set()
        episode_configs = []
        for config_tuple, group_data in filtered_grouped_data.items():
            config_dict = dict(config_tuple)
            key = (
                config_dict.get('profile'),
                config_dict.get('model'),
                config_dict.get('env'),
                config_dict.get('method'),
                config_dict.get('value'),
                config_dict.get('filter'),
            )
            if key in seen_keys:
                continue
            seen_keys.add(key)
            episode_configs.append(config_dict)

        # Sort configurations for stable, readable output
        episode_configs.sort(key=lambda x: (x['profile'], x['model'], x['env'], x['method'], x.get('filter') or '', x['value'] or 0))

        for config in episode_configs:
            config_tuple = tuple(sorted(config.items()))
            if config_tuple not in filtered_grouped_data:
                continue
            group_data = filtered_grouped_data[config_tuple]
            stats, n_experiments = calculate_statistics(group_data)

            # Calculate total episodes across experiments for this configuration
            total_episodes = 0
            for df in group_data:
                if 'num_episodes' in df.columns:
                    total_episodes += df['num_episodes'].sum()

            method_name = create_config_name(config)
            row = [
                config['profile'].title(),
                f"{config['model']} {config['env']}",
                method_name,
                str(n_experiments),
                str(int(total_episodes)),
            ]
            f.write("| " + " | ".join(row) + " |\n")

    # Write details.md
    details_file = os.path.join(args.output_dir, 'details.md')
    with open(details_file, 'w') as f:
        f.write("# Detailed Experimental Metrics\n")
    
    # Write each details table
    for table_data in details_tables:
        model = table_data['model']
        env = table_data['env']
        header_cols = table_data['header_cols']
        rows = table_data['rows']
        configs = table_data.get('configs', [None] * len(rows))

        # Treat filtered and unfiltered configurations as separate main results.
        main_rows = []
        seen_main_methods = set()

        for row, config in zip(rows, configs):
            if config is None:
                main_rows.append(row)
                continue

            method_key = (
                config['profile'],
                config['method'],
                config.get('value', None),
                config.get('filter', None),
            )

            if method_key not in seen_main_methods:
                main_rows.append(row)
                seen_main_methods.add(method_key)

        with open(details_file, 'a') as f:
            f.write(f"\n## {model} {env} Detailed Metrics\n\n")
            f.write("For each metric, cells are **mean ± sample standard deviation** "
                    "over episodes (`ddof=1`), in the format \"mean ± std\".\n\n")
            f.write("- **Mean Iterations to Converge**: Average number of iterations for "
                    "the root-finding algorithm to converge\n")
            f.write("- **Convergence Rate**: Fraction of root-finding attempts that "
                    "successfully converged\n")
            f.write("- **Outcome Fractions**: Fraction of decision steps with each "
                    "policy augmentation outcome\n\n")
            write_table_section(f, "Main Experimental Results", header_cols, main_rows)
    
    print(f"Analysis complete! Results written to:")
    print(f"  Summary: {summary_file}")
    print(f"  Details: {details_file}")


if __name__ == '__main__':
    main()
