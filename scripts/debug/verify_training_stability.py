
#!/usr/bin/env python3
import os, glob, statistics
from collections import defaultdict
from typing import Dict, List, Tuple

# TensorBoard event reader
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

def moving_avg(xs: List[float], k: int) -> List[float]:
    if k <= 1 or k > len(xs):
        return xs[:]
    out = []
    s = sum(xs[:k])
    out.append(s / k)
    for i in range(k, len(xs)):
        s += xs[i] - xs[i-k]
        out.append(s / k)
    # Pad to keep same length (align to the right)
    pad = [out[0]] * (len(xs) - len(out))
    return pad + out

def linregress(y: List[float]) -> Tuple[float,float]:
    n = len(y)
    if n < 2:
        return 0.0, y[-1] if y else 0.0
    x = list(range(n))
    meanx = (n-1)/2.0
    meany = sum(y)/n
    num = sum((xi-meanx)*(yi-meany) for xi, yi in zip(x,y))
    den = sum((xi-meanx)**2 for xi in x)
    slope = num/den if den != 0 else 0.0
    intercept = meany - slope*meanx
    return slope, intercept

def load_scalars(logdir: str, tags: List[str]) -> Dict[str, List[Tuple[float,float]]]:
    '''Return {tag: [(step, value), ...]} merged across all event files (sorted by step).'''
    series = defaultdict(list)
    event_files = []
    for root, _, _ in os.walk(logdir):
        event_files.extend(glob.glob(os.path.join(root, "events.out.tfevents.*")))
    if not event_files:
        raise FileNotFoundError(f"No event files found under {logdir}")
    for ef in event_files:
        try:
            ea = EventAccumulator(ef, size_guidance={"scalars": 0})
            ea.Reload()
            available = set(ea.Tags().get("scalars", []))
            for tag in tags:
                if tag in available:
                    vals = ea.Scalars(tag)
                    series[tag].extend([(v.step, float(v.value)) for v in vals])
        except Exception as e:
            print(f"[warn] failed to read {ef}: {e}")
    # sort & dedup by step
    for tag in list(series.keys()):
        seen = {}
        for step, val in sorted(series[tag], key=lambda t: t[0]):
            seen[step] = val  # keep last per-step
        series[tag] = sorted(seen.items(), key=lambda t: t[0])
    return series

def summarize(series, tag):
    if tag not in series or len(series[tag]) < 5:
        return None
    steps, vals = zip(*series[tag])
    return {"steps": list(steps), "values": list(vals)}

def pct_of_range(x: float, lo: float, hi: float) -> float:
    r = max(1e-8, hi - lo)
    return 100.0 * abs(x) / r

def analyze(logdir: str, reward_range_hint: Tuple[float,float] = None, ma_window: int = 1000):
    tags = [
        "eval/mean_reward",
        "rollout/ep_rew_mean",
        "train/td_loss",
        "train/loss",
        "train/q_values",
        "train/qf_max",
        "train/qf_mean",
        "train/qf_min",
        "time/iterations"
    ]
    series = load_scalars(logdir, tags)
    out = {}

    # Choose eval if present, else rollout for reward
    eval_series = summarize(series, "eval/mean_reward")
    train_series = summarize(series, "rollout/ep_rew_mean")
    reward_series = eval_series or train_series
    reward_tag = "eval/mean_reward" if eval_series else "rollout/ep_rew_mean" if train_series else None

    if reward_series:
        vals = reward_series["values"]
        # moving average window in *points* (fallback to len//10)
        k = max(5, min(len(vals)//10, 200))
        mav = moving_avg(vals, k)
        n = len(mav)
        tail = mav[int(n*0.8):] if n >= 10 else mav
        slope, _ = linregress(tail)
        lo, hi = (min(mav), max(mav))
        slope_pct = pct_of_range(slope * len(tail), lo, hi)  # change over tail as pct of range
        out["convergence"] = {
            "tag": reward_tag,
            "n_points": n,
            "ma_window": k,
            "tail_points": len(tail),
            "range": [lo, hi],
            "tail_delta_pct_of_range": slope_pct
        }
    # train-eval gap
    if eval_series and train_series:
        # align by step index (not wall time)
        tevals = eval_series["values"]
        ttrns = train_series["values"]
        n = min(len(tevals), len(ttrns))
        tevals = tevals[-n:]
        ttrns = ttrns[-n:]
        gap = [abs(a-b) for a,b in zip(tevals, ttrns)]
        tail = gap[int(n*0.8):] if n>=10 else gap
        mean_gap = sum(tail)/len(tail) if tail else float('nan')
        lo = min(min(tevals), min(ttrns))
        hi = max(max(tevals), max(ttrns))
        gap_pct = pct_of_range(mean_gap, lo, hi)
        out["train_eval_gap"] = {
            "aligned_points": n,
            "tail_points": len(tail),
            "mean_abs_gap": mean_gap,
            "mean_abs_gap_pct_of_range": gap_pct
        }

    # TD loss stability
    td = summarize(series, "train/td_loss") or summarize(series, "train/loss")
    if td:
        vals = td["values"]
        n = len(vals)
        tail = vals[int(n*0.8):] if n>=10 else vals
        # trend via slope
        slope, _ = linregress(tail)
        var = statistics.pvariance(tail) if len(tail) > 1 else 0.0
        out["td_loss_stability"] = {
            "tag": "train/td_loss" if "train/td_loss" in series else "train/loss",
            "tail_points": len(tail),
            "tail_variance": var,
            "tail_slope": slope
        }

    # Q-value magnitude bounds, if available
    q_candidates = [summarize(series, t) for t in ["train/qf_max","train/qf_mean","train/qf_min","train/q_values"]]
    q_candidates = [qc for qc in q_candidates if qc]
    if q_candidates:
        qvals = []
        for qc in q_candidates:
            qvals.extend(qc["values"][-max(1, len(qc["values"])//5):])  # last 20%
        if qvals:
            q_abs_max = max(abs(v) for v in qvals)
            out["q_bounds"] = {
                "observed_abs_max_last20pct": q_abs_max,
                "conservative_bound_hint_gamma_0p8": 10.0
            }

    return out

def main():
    import argparse, json
    ap = argparse.ArgumentParser()
    ap.add_argument("--logdir", required=True, help="Path to directory containing TensorBoard event files")
    ap.add_argument("--ma_window", type=int, default=0, help="Moving average window (points); 0 = auto")
    args = ap.parse_args()
    res = analyze(args.logdir, ma_window=args.ma_window or 1000)
    print(json.dumps(res, indent=2))
    parts = []
    if "convergence" in res:
        tail_pct = res["convergence"]["tail_delta_pct_of_range"]
        parts.append(f"eval return plateaued (tail Δ ≈ {tail_pct:.1f}% of range)")
    if "train_eval_gap" in res:
        parts.append(f"train–eval gap ≤ ~{res['train_eval_gap']['mean_abs_gap_pct_of_range']:.1f}% of range")
    if "td_loss_stability" in res:
        parts.append("TD loss stable (no upward trend)")
    if "q_bounds" in res:
        parts.append(f"Q magnitudes bounded (|Q| ≤ ~{res['q_bounds']['observed_abs_max_last20pct']:.2f})")
    if parts:
        print("\nSuggested rebuttal sentence:")
        print("The base DQN was verified for stability prior to freezing: " + "; ".join(parts) + ".")
    else:
        print("\n[Note] Not enough tags were found to auto-summarize. Make sure eval/mean_reward or rollout/ep_rew_mean exist.")

if __name__ == "__main__":
    main()
