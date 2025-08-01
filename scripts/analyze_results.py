#!/usr/bin/env python3
"""
Analysis script for norm supervisor experiment results.
Scans CSV files in results directory and generates summary statistics.
"""

import os
import pandas as pd
import numpy as np
from collections import defaultdict
import argparse

import matplotlib
matplotlib.use('pgf')  # Use pgf backend to render text in LaTeX
import matplotlib.pyplot as plt

plt.rcParams.update({
    "text.usetex": True,
    "pgf.texsystem": "pdflatex",
    "pgf.rcfonts": False,  # don't override LaTeX document fonts
    "font.family": "serif",  # use whatever LaTeX is using (Times here)
    "text.latex.preamble": r"\usepackage{times}",
})

# CMYK-safe, WCAG 2.0-compliant, grayscale distinguishable color codes
colors = {
    "edge": "white",
    "gray": "#949494",
    "medium_gray": "#949494",
    "dark_gray": "#474747",
    "purple": "#542c5d", #88007d",
    "teal": "#008381" #"#007f7c" #007f7f",
}

patterns = {
    "unsupervised": "",
    "cautious": "",
    "efficient": ""
}
EDGE_WIDTH = 0.01

# Utility function to compute left/right lane preferences for any number of lanes
def compute_left_right_lane_preferences(stats, n_lanes=None):
    """Given a stats dict (col: (mean, std)), compute left/right lane preferences and their std errors."""
    # Find all lane_X_preference columns
    lane_cols = sorted([col for col in stats.keys() if col.startswith('lane_') and col.endswith('_preference')],
                       key=lambda x: int(x.split('_')[1]))
    if not lane_cols:
        return None, None, None, None
    if n_lanes is None:
        n_lanes = len(lane_cols)
    half = n_lanes // 2
    left_cols = lane_cols[:half]
    right_cols = lane_cols[half:]
    # Sum means and propagate std errors (sqrt of sum of variances)
    left_mean = sum(stats[col][0] for col in left_cols if col in stats)
    right_mean = sum(stats[col][0] for col in right_cols if col in stats)
    left_std = np.sqrt(sum((stats[col][1] ** 2) for col in left_cols if col in stats))
    right_std = np.sqrt(sum((stats[col][1] ** 2) for col in right_cols if col in stats))
    return left_mean, left_std, right_mean, right_std


def list_csv_files(directory):
    """List all CSV files in the given directory and subdirectories, skipping any 'ignore' directories."""
    if not os.path.exists(directory):
        return []
    
    csv_files = []
    for root, dirs, files in os.walk(directory):
        # Skip any directory named 'ignore'
        if 'ignore' in dirs:
            dirs.remove('ignore')
        if os.path.basename(root) == 'ignore':
            continue
        for file in files:
            if file.endswith('.csv'):
                # Get relative path from the results directory
                rel_path = os.path.relpath(os.path.join(root, file), directory)
                csv_files.append(rel_path)
    
    return sorted(csv_files)


def parse_configuration_from_filename(filename):
    """Parse configuration from filename format: profile/method/model_env_value.csv"""
    base = os.path.basename(filename)
    name, _ = os.path.splitext(base)
    parts = name.split('_')
    
    model = parts[0]
    env = parts[1]
    value = None
    if len(parts) > 2:
        try:
            value = float(parts[2])
        except ValueError:
            value = None
    
    # Get method from parent directory
    method = os.path.basename(os.path.dirname(filename))
    # Remove _filtered/_unfiltered suffix for label purposes
    if method.endswith('_filtered'):
        method_base = method[:-9]
        filtered = True
    elif method.endswith('_unfiltered'):
        method_base = method[:-11]
        filtered = False
    else:
        method_base = method
        filtered = False
    
    # Get profile from grandparent directory
    profile = os.path.basename(os.path.dirname(os.path.dirname(filename)))
    
    return {
        'profile': profile,
        'method': method_base,
        'filtered': filtered,
        'value': value,
        'model': model,
        'env': env,
        'mode': method_base if method_base in ['default', 'naive', 'nop'] else 'default',
        'filename': filename
    }


def load_and_group_data(results_dir):
    """Load all CSV files and group by configuration."""
    csv_files = list_csv_files(results_dir)
    
    if not csv_files:
        print(f"No CSV files found in '{results_dir}'")
        return {}
    
    grouped_data = defaultdict(list)
    
    for filename in csv_files:
        config = parse_configuration_from_filename(filename)
        if config is None:
            print(f"Warning: Could not parse configuration from filename: {filename}")
            continue
        
        filepath = os.path.join(results_dir, filename)
        try:
            df = pd.read_csv(filepath)
            if not df.empty:
                # Add configuration info to each row
                for key, value in config.items():
                    df[key] = value
                grouped_data[tuple(sorted(config.items()))].append(df)
        except Exception as e:
            print(f"Warning: Could not read {filename}: {e}")
    
    return grouped_data


def calculate_statistics(group_data):
    """Calculate mean and standard deviation for all numeric columns."""
    # Combine all dataframes in the group
    combined_df = pd.concat(group_data, ignore_index=True)
    
    # Get numeric columns (excluding configuration columns)
    config_cols = ['profile', 'method', 'value', 'model', 'env', 'mode']
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
    
    return stats, len(combined_df)


def format_statistic(mean_val, std_val, n_experiments, metric_name=None):
    """Format mean and standard error as 'mean ± SE'."""
    if pd.isna(mean_val) or pd.isna(std_val) or n_experiments <= 1:
        return "-"
    
    # Calculate standard error
    se_val = std_val / np.sqrt(n_experiments)
    return f"{mean_val:.2f} ± {se_val:.2f}"


def format_median_iqr(median_val, q1_val, q3_val, iqr_val):
    """Format median and IQR as "median (Q1Q3)"."""
    if pd.isna(median_val) or pd.isna(q1_val) or pd.isna(q3_val) or pd.isna(iqr_val):
        return "-"
    
    return f"{median_val:.2f} ({q1_val:.2f} - {q3_val:.2f})"


def format_collision_rate(group_data):
    """Format collision rate per hour."""
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
        # Calculate collision rate per hour
        total_time_hours = total_time_seconds / 3600
        collision_rate = total_collisions / total_time_hours
        # NOTE: We can model the collision data as a binomial distribution where each episode is a
        # trial that either ends with success (no collision) or failure (collision).
        n = sum([df['num_episodes'].sum() for df in group_data]) # n  = total number of trials
        p = total_collisions / n                                 # p  = probability of a collision
        se_p = np.sqrt(p * (1 - p) / n)                          # SE = sqrt(n*p*(1-p)) / n
        # NOTE: We can propagate the standard error to a linear function of p:
        # f(p) = (p * 3600) / (ep_length * policy_period)
        # |df/dp| = 3600 / (ep_length * policy_period)
        # se_f = |df/dp| * se_p = (3600 * se_p) / (ep_length * policy_period)
        mean_episode_length = total_time_seconds / n if n > 0 else 1
        se_collision_rate = (3600 * se_p) / (mean_episode_length * policy_period)
        return f"{collision_rate:.2f} ± {se_collision_rate:.2f}"


def get_lane_columns(stats):
    """Get lane time columns from statistics."""
    return sorted([col for col in stats.keys() if col.startswith('lane_') and col.endswith('_preference')])


def compute_success_rate(group_data):
    """Compute success rate as percentage of episodes without collision."""
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
    """Create a readable configuration name."""
    if config_dict['method'] in ['adaptive', 'fixed'] and config_dict['value'] is not None:
        # Format value as power of 10
        value = config_dict['value']
        if value == 0.01:
            value_str = "10⁻²"
        elif value == 0.0316:
            value_str = "10⁻¹·⁵"
        elif value == 0.10:
            value_str = "10⁻¹"
        elif value == 0.3162:
            value_str = "10⁻⁰·⁵"
        elif value == 1.00:
            value_str = "10⁰"
        else:
            value_str = str(value)
        return f"{config_dict['method'].title()} ({value_str})"
    elif config_dict['method'] == 'naive':
        return f"{config_dict['method'].title()}"
    else:
        return f"{config_dict['method'].title()}"


def method_sort_key(config):
    """Sort key for methods."""
    method = config.get('method', '').lower()
    value = config.get('value', 0)
    # Unsupervised first
    if method == 'unsupervised':
        return (0, 0, 0)
    # Filter Only second
    elif method == 'filter_only':
        return (1, 0, 0)
    # Naive third
    elif method == 'naive':
        return (2, 0, 0)
    # Adaptive next, sorted by value
    elif method == 'adaptive':
        return (3, 0, float(value) if value is not None else 0)
    # Fixed next, sorted by value
    elif method == 'fixed':
        return (4, 0, float(value) if value is not None else 0)
    # Default fallback
    else:
        return (99, 0, 0)


def generate_markdown_tables(grouped_data):
    """Generate markdown tables from grouped data, one per model-environment combination."""
    
    # Define metric categories and their display names
    summary_metric_categories = {
        'Core Metrics': ['collision_rate', 'cost_rate', 'mean_speed']
    }
    
    details_metric_categories = {
        'Violation Rates': [
            'speed_violation_rate', 'tailgating_violation_rate',
            'braking_violation_rate', 'lane_keeping_violation_rate',
            'lane_change_tailgating_violation_rate', 'lane_change_braking_violation_rate',
            'collision_violation_rate', 'lane_change_collision_violation_rate'
        ],
        'Cost Metrics': ['cost_rate']
    }
    
    # Create display names mapping
    display_names = {
        # Summary metrics
        'mean_episode_length'    : 'Episode Length (s)',
        'collision_rate'         : 'Collision Rate (hr⁻¹)',
        'mean_speed'             : 'Speed (m/s)',
        'cost_rate'              : 'Cost Rate (hr⁻¹)',
        'avoided_cost_rate'      : 'Avoided Cost Rate (hr⁻¹)',
        
        # Details metrics
        'speed_violation_rate'                 : 'Speed Violations (hr⁻¹)',
        'tailgating_violation_rate'            : 'Tailgating Violations (hr⁻¹)',
        'braking_violation_rate'               : 'Braking Violations (hr⁻¹)',
        'lane_keeping_violation_rate'          : 'LaneKeeping Violations (hr⁻¹)',
        'lane_change_tailgating_violation_rate': 'Lane Change Tailgating Violations (hr⁻¹)',
        'lane_change_braking_violation_rate'   : 'Lane Change Braking Violations (hr⁻¹)',
        'collision_violation_rate'             : 'Collision Violations (hr⁻¹)',
        'lane_change_collision_violation_rate' : 'Lane Change Collision Violations (hr⁻¹)',
        
        # Lane usage metrics (old, will be replaced)
        # 'lane_0_preference': 'Left Lane Preference (%)',
        # 'lane_1_preference': 'Right Lane Preference (%)'
    }
    # Add new left/right lane preference display names
    display_names['left_lane_preference'] = 'Left Lane Preference (%)'
    display_names['right_lane_preference'] = 'Right Lane Preference (%)'
    


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
                # Compute left/right lane preferences
                left_mean, left_std, right_mean, right_std = compute_left_right_lane_preferences(stats)
                # Build summary data row
                summary_row = [config_name]
                for category, metrics in summary_metric_categories.items():
                    for metric in metrics:
                        if metric == 'collision_rate':
                            summary_row.append(format_collision_rate(group_data))


                        elif metric in stats:
                            mean_val, std_val = stats[metric]
                            if metric in ['cost_rate']:
                                mean_val *= 3600
                                std_val *= 3600
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
                            if 'violation_rate' in metric or 'cost_rate' in metric:
                                mean_val *= 3600
                                std_val *= 3600
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
    """Generate a summary table showing experiment counts and total episodes for each configuration."""
    summary_rows = []
    seen_keys = set()
    
    # Collect all unique configurations
    all_configs = []
    for config_tuple, group_data in grouped_data.items():
        config_dict = dict(config_tuple)
        key = (config_dict['profile'], config_dict['model'], config_dict['env'], 
               config_dict['method'], config_dict['value'], config_dict['filtered'])
        if key in seen_keys:
            continue
        seen_keys.add(key)
        # Only include in summary if it's a main result (not ablation)
        if config_dict['method'] in ['unsupervised', 'filter_only', 'nop'] or config_dict['filtered'] == True:
            all_configs.append(config_dict)
    
    # Sort configurations
    all_configs.sort(key=lambda x: (x['profile'], x['model'], x['env'], x['method'], x['value'] or 0))
    
    for config in all_configs:
        config_tuple = tuple(sorted(config.items()))
        if config_tuple in grouped_data:
            group_data = grouped_data[config_tuple]
            stats, n_experiments = calculate_statistics(group_data)
            
            # Calculate total episodes
            total_episodes = 0
            for df in group_data:
                if 'num_episodes' in df.columns:
                    total_episodes += df['num_episodes'].sum()
            
            # Calculate success rate
            success_rate = compute_success_rate(group_data)
            method_name = create_config_name(config)
            
            # Create row
            row = [
                config['profile'].title(),
                f"{config['model']} {config['env']}",
                method_name,
                str(n_experiments),
                str(total_episodes),
                success_rate
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


def generate_adaptive_trend_plot(grouped_data, output_dir, adaptive_values, title, projection_point):
    """Generate line plots showing how metrics evolve with adaptive method values."""
    # Create plots subdirectory
    plots_dir = os.path.join(output_dir, 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    
    # Group data by model-environment-profile combination
    model_env_profile_groups = defaultdict(lambda: defaultdict(dict))
    for config_tuple, group_data in grouped_data.items():
        config_dict = dict(config_tuple)
        if config_dict['method'] != 'adaptive' or not config_dict['filtered']:
            continue
        
        model_env_key = (config_dict['model'], config_dict['env'])
        profile = config_dict['profile']
        value = config_dict.get('value')
        
        if value is not None and value in adaptive_values:
            model_env_profile_groups[model_env_key][profile][value] = group_data
    
    # Generate plots for each model-environment combination
    for (model, env), profile_configs in sorted(model_env_profile_groups.items()):
        if 'cautious' not in profile_configs:
            continue
        
        # Create subplots with shared x-axis to fit in a single column
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(3.25, 3.5), sharex=True)

        SUPTITLE_FONTSIZE = 10
        LABEL_FONTSIZE = 9      
        LEGEND_FONTSIZE = 8
        TICK_FONTSIZE = 8
        MARKER_SIZE = 2.5
        ERRORBAR_LINEWIDTH = 1.2
        
        # Only plot cautious profile
        profile = 'cautious'
        profile_configs = profile_configs[profile]
        
        # Plot data for cautious profile
        x_collision = []
        y_collision_values = []
        y_collision_errors = []
        x_cost = []
        y_cost_values = []
        y_cost_errors = []
        
        # Collect data points for adaptive values
        for value in sorted(adaptive_values):
            if value in profile_configs:
                group_data = profile_configs[value]
                stats, n_experiments = calculate_statistics(group_data)
                
                # Get collision rate per hour
                collision_rate_str = format_collision_rate(group_data)
                if collision_rate_str != "0.00":
                    try:
                        # Parse collision rate from format "X.XX ± Y.YY" or "X.XX"
                        if "±" in collision_rate_str:
                            parts = collision_rate_str.split("±")
                            collision_rate = float(parts[0].strip())
                            collision_error = float(parts[1].strip())
                        else:
                            collision_rate = float(collision_rate_str)
                            collision_error = 0  # No error info available
                        x_collision.append(value)
                        y_collision_values.append(collision_rate)
                        y_collision_errors.append(collision_error)
                    except ValueError:
                        pass
                # Get cost rate (raw, before 3600 multiplication)
                if 'cost_rate' in stats:
                    mean_val, std_val = stats['cost_rate']
                    if not pd.isna(mean_val):
                        # Convert to per-hour units
                        cost_rate = mean_val * 3600
                        # Compute standard error: std / sqrt(n), then convert to per-hour
                        se_val = std_val / np.sqrt(n_experiments) if n_experiments > 1 else 0
                        se_val *= 3600  # Convert error to per-hour units
                        x_cost.append(value)
                        y_cost_values.append(cost_rate)
                        y_cost_errors.append(se_val)
        
        # Only plot if we have data
        if x_collision and y_collision_values:
            ax1.errorbar(x_collision, y_collision_values, yerr=y_collision_errors, 
                       marker='s', color='black', linestyle=':',
                       capsize=3, capthick=1, linewidth=ERRORBAR_LINEWIDTH, markersize=MARKER_SIZE)
        
        if x_cost and y_cost_values:
            ax2.errorbar(x_cost, y_cost_values, yerr=y_cost_errors, 
                       marker='s', color='black', linestyle=':',
                       capsize=3, capthick=1, linewidth=ERRORBAR_LINEWIDTH, markersize=MARKER_SIZE)
        
        # Use log scale for x-axis if values span multiple orders of magnitude
        if max(adaptive_values) / min(adaptive_values) > 10:
            ax1.set_xscale('log')
            ax2.set_xscale('log')
        
        # Add grid
        ax1.grid(True, alpha=0.3)
        ax2.grid(True, alpha=0.3)

        # Add vertical dashed line at projection point
        for ax in [ax1, ax2]:
            ax.axvline(x=projection_point, color='gray', linestyle='--', linewidth=1.2, alpha=0.6)

        ax1.set_ylabel(r"Collision Rate $\left(\mathrm{hr}^{-1}\right)$", fontsize=LABEL_FONTSIZE)
        ax2.set_ylabel(r"Cost Rate $\left(\mathrm{hr}^{-1}\right)$", fontsize=LABEL_FONTSIZE)
        ax2.set_xlabel(r"KL Budget $\left(\bar\delta\right)$", fontsize=LABEL_FONTSIZE)
        fig.suptitle(title, fontsize=SUPTITLE_FONTSIZE, y=0.96)
        for ax in [ax1, ax2]:
            ax.tick_params(axis='both', which='major', labelsize=TICK_FONTSIZE)

        plt.tight_layout()
        fig.align_ylabels([ax1, ax2])
        for ax in [ax1, ax2]:
            xmin, xmax = ax.get_xlim()
            ax.axvspan(projection_point, xmax, color='gray', alpha=0.2, label='Cost-Optimal\nProjection')
            ax.set_xlim(xmin, xmax)

        # Add a shared legend across the top, under the title
        ax1.legend(loc='upper right', fontsize=LEGEND_FONTSIZE)
    
        plot_file = os.path.join(plots_dir, f'adaptive_trends_{model}_{env}.pdf')
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Adaptive trends plot saved to: {plot_file}")


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
        δ value to pick for the adaptive β experiments (default 1.0).
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

    This plot compares three experiment configurations for every model–environment
    combination:
        1. Unsupervised baseline.
        2. Cautious profile – Adaptive (δ = *selected_value*) – *filtered*.
        3. Efficient profile – Adaptive (δ = *selected_value*) – *filtered*.
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

        # Unsupervised baseline (profile agnostic)
        if cfg.get("method") == "unsupervised":
            groups_by_model_env[key]["unsupervised"].extend(group_data)

        # Adaptive β (δ = selected_value), filtered
        elif (
            cfg.get("method") == "adaptive"
            and cfg.get("filtered", False)
            and abs(float(cfg.get("value", 0)) - float(selected_value)) < 1e-6
        ):
            if cfg.get("profile") == "cautious":
                groups_by_model_env[key]["cautious_adaptive"].extend(group_data)
            elif cfg.get("profile") == "efficient":
                groups_by_model_env[key]["efficient_adaptive"].extend(group_data)

    # Helper to compute mean & SE for a single column across a list of dfs
    def _mean_se(dfs, col):
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
        se = (series.std() / np.sqrt(len(series))) if len(series) > 1 else 0.0
        return mean, se

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

        # Collect statistics
        stats = {key: {"means": [], "ses": []} for key in data_dict.keys()}
        for cat in categories:
            col_name = f"{ACTION_PREFIX}{cat}{ACTION_SUFFIX}"
            for key in stats.keys():
                mean, se = _mean_se(data_dict[key], col_name)
                stats[key]["means"].append(mean)
                stats[key]["ses"].append(se)

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
            #edgecolor=colors['edge'],
            hatch=patterns['unsupervised'],
            capsize=CAPS_SIZE,
        )
        ax.bar(
            ind,
            stats["cautious_adaptive"]["means"],
            width,
            yerr=stats["cautious_adaptive"]["ses"],
            label=r"Cautious",
            color=colors['teal'],
            edgecolor=colors['edge'],
            linewidth=EDGE_WIDTH,
            hatch=patterns['cautious'],
            capsize=CAPS_SIZE,
        )
        ax.bar(
            ind + width,
            stats["efficient_adaptive"]["means"],
            width,
            yerr=stats["efficient_adaptive"]["ses"],
            label=r"Efficient",
            color=colors['purple'],
            edgecolor=colors['edge'],
            linewidth=EDGE_WIDTH,
            hatch=patterns['efficient'],
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


# ---------------------------------------------------------------------
# Lane-occupancy stacked bar chart
# ---------------------------------------------------------------------


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
    TICK_FONTSIZE = 8
    LEGEND_FONTSIZE = 7
    LEGEND_TITLE_FONTSIZE = 7
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

        if cfg.get("method") == "unsupervised":
            groups_by_model_env[key]["unsupervised"].extend(gdata)
        elif (
            cfg.get("method") == "adaptive"
            and cfg.get("filtered", False)
            and abs(float(cfg.get("value", 0)) - float(selected_value)) < 1e-6
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
    parser = argparse.ArgumentParser(description='Analyze experiment results from CSV files')
    parser.add_argument('--results-dir', default=None, 
                       help='Directory containing CSV result files (default: script_dir/../results)')
    parser.add_argument('--output-dir', default=None,
                       help='Output directory for analysis files (default: script_dir/../analysis)')
    parser.add_argument('--fixed-values', default='0.01, 0.10, 1.00',
                       help='Comma-separated list of allowed values for fixed method (e.g., 0.01,0.05,0.1)')
    parser.add_argument('--adaptive-values', default='0.01, 0.10, 1.00',
                       help='Comma-separated list of allowed values for adaptive method (e.g., 0.01,0.05,0.1)')
    parser.add_argument('--plot-adaptive-values', default='0.01, 0.0316, 0.10, 0.3162, 1.00, 3.1623, 10.000',
                       help='Comma-separated list of adaptive values to include in trend plots')
    
    args = parser.parse_args()
    
    # Get script directory for relative paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Set default paths relative to project root
    if args.results_dir is None:
        args.results_dir = os.path.join(project_root, 'results')
    if args.output_dir is None:
        args.output_dir = os.path.join(project_root, 'analysis')
    
    # Parse allowed values for fixed and adaptive methods
    def parse_value_list(val):
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
    
    # Generate adaptive trends plot
    if plot_adaptive_values:
        print("Generating adaptive trends plot...")
        generate_adaptive_trend_plot(
            grouped_data=grouped_data,
            output_dir=args.output_dir,
            adaptive_values=plot_adaptive_values,
            title=r"""Effect of KL Budget in Adaptive-$\beta$ SCPS
            in Simple Zero-Shot Environment""",
        projection_point=1.0)
    
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
        
        # Find the index of 'Collision Rate (hr⁻¹)' in the header
        try:
            collision_idx = header_cols.index('Collision Rate (hr⁻¹)')
        except ValueError:
            collision_idx = 1
        
        # Insert 'Success Rate (%)' before collision rate in header
        extended_header_cols = header_cols[:collision_idx] + ['Success Rate (%)'] + header_cols[collision_idx:]
        
        # Split rows into main and ablation
        main_rows = []
        ablation_rows = []
        seen_main_methods = set()
        
        for row, config in zip(rows, configs):
            if config is None:
                main_rows.append(row[:collision_idx] + [''] + row[collision_idx:])
                ablation_rows.append(row[:collision_idx] + [''] + row[collision_idx:])
                continue
            
            method_key = (config['profile'], config['method'], config.get('value', None))
            config_tuple = tuple(sorted(config.items()))
            group_data = filtered_grouped_data.get(config_tuple, None)
            success_rate = compute_success_rate(group_data) if group_data is not None else "-"
            new_row = row[:collision_idx] + [success_rate] + row[collision_idx:]
            
            if config['method'] in ['unsupervised', 'filter_only', 'nop']:
                if method_key not in seen_main_methods:
                    main_rows.append(new_row)
                    seen_main_methods.add(method_key)
            elif config['filtered'] == False:
                ablation_rows.append(new_row)
            else:
                if method_key not in seen_main_methods:
                    main_rows.append(new_row)
                    seen_main_methods.add(method_key)
        
        with open(summary_file, 'a') as f:
            f.write(f"\n## {model} {env} Results\n\n")
            write_table_section(f, "Main Experimental Results", extended_header_cols, main_rows)
            if any(cell for row in ablation_rows for cell in row if cell and not cell[0:2] == '**'):
                write_table_section(f, "Ablation Studies", extended_header_cols, ablation_rows)
    
    # Write summary table
    with open(summary_file, 'a') as f:
        f.write("\n## Experiment Summary\n\n")
        f.write("| Profile | Model-Environment | Method | Experiments | Total Episodes |\n")
        f.write("|---------|-------------------|--------|-------------|----------------|\n")
        for row in summary_rows:
            f.write("| " + " | ".join(row[:5]) + " |\n")

    # Write ablation studies table
    ablation_configs = []
    for config_tuple, group_data in filtered_grouped_data.items():
        config_dict = dict(config_tuple)
        if config_dict.get('method', 'nop') not in ['unsupervised', 'filter_only', 'nop'] and not config_dict.get('filtered', True):
            ablation_configs.append(config_dict)
    
    ablation_configs.sort(key=lambda x: (x['profile'], x['model'], x['env'], x['method'], x['value'] or 0))
    
    if ablation_configs:
        with open(summary_file, 'a') as f:
            f.write("\n## Ablation Studies\n\n")
            f.write("| Profile | Model-Environment | Method | Experiments | Total Episodes |\n")
            f.write("|---------|-------------------|--------|-------------|----------------|\n")
            for config in ablation_configs[::-1]:
                config_tuple = tuple(sorted(config.items()))
                if config_tuple in filtered_grouped_data:
                    group_data = filtered_grouped_data[config_tuple]
                    stats, n_experiments = calculate_statistics(group_data)
                    
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
                        str(total_episodes)
                    ]
                    f.write("| " + " | ".join(row) + " |\n")
    
    # Write details.md
    details_file = os.path.join(args.output_dir, 'details.md')
    with open(details_file, 'w') as f:
        f.write("# Norm Violation Details\n")
    
    # Write each details table
    for table_data in details_tables:
        model = table_data['model']
        env = table_data['env']
        header_cols = table_data['header_cols']
        rows = table_data['rows']
        configs = table_data.get('configs', [None] * len(rows))
        
        # Split rows into main and ablation
        main_rows = []
        ablation_rows = []
        seen_main_methods = set()
        
        for row, config in zip(rows, configs):
            if config is None:
                main_rows.append(row)
                ablation_rows.append(row)
                continue
            
            method_key = (config['profile'], config['method'], config.get('value', None))
            
            if config['method'] in ['unsupervised', 'filter_only', 'nop']:
                if method_key not in seen_main_methods:
                    main_rows.append(row)
                    seen_main_methods.add(method_key)
            elif config['filtered'] == False:
                ablation_rows.append(row)
            else:
                if method_key not in seen_main_methods:
                    main_rows.append(row)
                    seen_main_methods.add(method_key)
        
        with open(details_file, 'a') as f:
            f.write(f"\n## {model} {env} Violation Rates\n\n")
            f.write("For each metric, the mean and standard error between experiments are given in "
                    "the format \"mean ± SE\". \n\n")
            write_table_section(f, "Main Experimental Results", header_cols, main_rows)
            if any(cell for row in ablation_rows for cell in row if cell and not cell.startswith('**')):
                write_table_section(f, "Ablation Studies", header_cols, ablation_rows)
    
    print(f"Analysis complete! Results written to:")
    print(f"  Summary: {summary_file}")
    print(f"  Details: {details_file}")


if __name__ == '__main__':
    main()
