#!/bin/bash

# SCPS experiment matrix for the merge environment (mirror of run_experiments.sh).

NUM_EPISODES=1000

if [ $# -ge 1 ]; then
    ENVIRONMENTS=("$1")
else
    ENVIRONMENTS=("MERGE_BASIC")
fi

# Optional: pass a model path as the second argument (zip or directory with model.zip).
MODEL_PATH_ARG=""
if [ $# -ge 2 ]; then
    MODEL_PATH_ARG="--model-path $2"
fi

# Set to true to overwrite existing results
FORCE_WRITE=true

experiments=(
    # BASELINES
    # <profile>         <method>    <value>  <filter>
    " merge_courtesy  nop             nan  False "  # Unsupervised
    " merge_courtesy  nop             nan  True  "  # Filter-only
    " merge_courtesy  naive           nan  False "
    " merge_courtesy  naive           nan  True  "

    # ADAPTIVE
    # <profile>         <method>    <value>  <filter>
    " merge_courtesy  adaptive       0.05  False "
    " merge_courtesy  adaptive       0.01  True  "
    " merge_courtesy  adaptive       0.02  True  "
    " merge_courtesy  adaptive       0.03  True  "
    " merge_courtesy  adaptive       0.05  True  "

    # FIXED
    # <profile>         <method>    <value>  <filter>
    " merge_courtesy  fixed          1.00  False "
    " merge_courtesy  fixed          1.00  True  "

    # PROJECTION
    # <profile>         <method>    <value>  <filter>
    " merge_courtesy  projection      nan  False "
    " merge_courtesy  projection      nan  True  "

    # LOG SPACED TRIALS
    # <profile>         <method>    <value>  <filter>
    #" merge_courtesy  adaptive     0.0316  True  "
    #" merge_courtesy  adaptive     0.3162  True  "
    #" merge_courtesy  adaptive     3.1623  True  "
   # " merge_courtesy  adaptive     10.000  True  "
    )

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

for ENV in "${ENVIRONMENTS[@]}"; do

    mkdir -p "$PROJECT_ROOT/results/$ENV"

    for args in "${experiments[@]}"; do
        # Each experiment line: <profile> <method> <value> <filter>
        read profile method value filter_flag_str <<< "$args"

        filter_flag=""
        if [ "$filter_flag_str" == "True" ]; then
            sub_dir="${method}_filtered"
            filter_flag="--filter"
        else
            sub_dir="${method}_unfiltered"
        fi

        mkdir -p "$PROJECT_ROOT/results/${ENV}/${profile}/${sub_dir}"

        file_prefix="MERGE_${ENV}"
        if [ "$method" == "adaptive" ] || [ "$method" == "fixed" ]; then
            out_path="$PROJECT_ROOT/results/${ENV}/${profile}/${sub_dir}/${file_prefix}_${value}.csv"
        else
            out_path="$PROJECT_ROOT/results/${ENV}/${profile}/${sub_dir}/${file_prefix}.csv"
        fi

        if [ "$FORCE_WRITE" = true ] && [ -f "$out_path" ]; then
            echo "Overwriting existing results: $out_path"
        elif [ -f "$out_path" ]; then
            echo "Skipping existing results: $out_path"
            continue
        fi

        if [ "$method" == "adaptive" ] || [ "$method" == "fixed" ]; then
            echo "Running ${profile} ${method} (${sub_dir}) with value=${value} -> $out_path"
            python3 "$SCRIPT_DIR/test_merge.py" \
                --profile "$profile" \
                --method "$method" \
                --value "$value" \
                --episodes "$NUM_EPISODES" \
                --env "$ENV" \
                --output "$out_path" \
                $MODEL_PATH_ARG \
                $filter_flag
        else
            echo "Running ${profile} ${method} (${sub_dir}) -> $out_path"
            python3 "$SCRIPT_DIR/test_merge.py" \
                --profile "$profile" \
                --method "$method" \
                --episodes "$NUM_EPISODES" \
                --env "$ENV" \
                --output "$out_path" \
                $MODEL_PATH_ARG \
                $filter_flag
        fi
    done
done

echo "All merge runs completed!"
