#!/bin/bash

# Constants for episodes
NUM_EPISODES=1000

if [ $# -ge 1 ]; then
    ENVIRONMENTS=("$1")
else
    ENVIRONMENTS=("3L30V")
fi

# Set to true to overwrite existing results
FORCE_WRITE=false

experiments=(
    # BASELINES
    # <profile>   <method>    <value>  <filter>
    " right_lane  nop             nan  False "  # Unsupervised
    " right_lane  nop             nan  True  "  # Filter-only
    " right_lane  naive           nan  False " 
    " right_lane  naive           nan  True  "

    # ADAPTIVE
    # <profile>   <method>    <value>  <filter>
    " right_lane  adaptive       0.05  False "
    " right_lane  adaptive       0.05  True  "

    # FIXED
    # <profile>   <method>    <value>  <filter>
    " right_lane  fixed          0.75  False  "
    " right_lane  fixed          0.75  True  "

    # PROJECTION
    # <profile>   <method>    <value>  <filter>
    " right_lane  projection      nan  False "
    " right_lane  projection      nan  True  "

    # LOG SPACED TRIALS
    # <profile>   <method>    <value>  <filter>
    " right_lane  adaptive     0.00001  True  "
    " right_lane  adaptive     0.0000316  True  "
    " right_lane  adaptive     0.0001  True  "
    " right_lane  adaptive     0.000316  True  "
    " right_lane  adaptive     0.0010  True  "
    " right_lane  adaptive     0.0032  True  "
    " right_lane  adaptive     0.0100  True  "
    " right_lane  adaptive     0.0316  True  "
    " right_lane  adaptive     0.1000  True  "
    " right_lane  adaptive     0.3162  True  "
    " right_lane  adaptive     1.0000  True  "
    " right_lane  adaptive     3.1623  True  "
    " right_lane  adaptive     10.000  True  "
    " right_lane  adaptive     31.623  True  "
    " right_lane  adaptive     100.00  True  "
)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULTS_ROOT="$PROJECT_ROOT/results/highway"

for ENV in "${ENVIRONMENTS[@]}"; do

    # Create results directory for this environment if it doesn't exist
    mkdir -p "$RESULTS_ROOT/$ENV"
    
    for args in "${experiments[@]}"; do
        # Each experiment line: <profile> <method> <value> <filter>
        read profile method value filter_flag_str <<< "$args"

        # Determine filtered/unfiltered suffix and CLI flag
        filter_flag=""
        if [ "$filter_flag_str" == "True" ]; then
            sub_dir="${method}_filtered"
            filter_flag="--filter"
        else
            sub_dir="${method}_unfiltered"
        fi

        # Create subdirectory with profile prefix
        mkdir -p "$RESULTS_ROOT/${ENV}/${profile}/${sub_dir}"
        
        # Build output filename
        file_prefix="3L30V_${ENV}"
        if [ "$method" == "adaptive" ] || [ "$method" == "fixed" ]; then
            out_path="$RESULTS_ROOT/${ENV}/${profile}/${sub_dir}/${file_prefix}_${value}.csv"
        else
            out_path="$RESULTS_ROOT/${ENV}/${profile}/${sub_dir}/${file_prefix}.csv"
        fi

        if [ "$FORCE_WRITE" = true ] && [ -f "$out_path" ]; then
            echo "Overwriting existing results: $out_path"
        elif [ -f "$out_path" ]; then
            echo "Skipping existing results: $out_path"
            continue
        fi

        if [ "$method" == "adaptive" ] || [ "$method" == "fixed" ]; then
            echo "Running ${profile} ${method} (${sub_dir}) with value=${value} -> $out_path"
            python3 "$SCRIPT_DIR/test_highway.py" \
                --profile "$profile" \
                --method "$method" \
                --value "$value" \
                --episodes "$NUM_EPISODES" \
                --env "$ENV" \
                --output "$out_path" \
                $filter_flag
        else
            echo "Running ${profile} ${method} (${sub_dir}) -> $out_path"
            python3 "$SCRIPT_DIR/test_highway.py" \
                --profile "$profile" \
                --method "$method" \
                --episodes "$NUM_EPISODES" \
                --env "$ENV" \
                --output "$out_path" \
                $filter_flag
        fi
    done  # end experiments loop
done      # end env loop

echo "All runs completed!"
