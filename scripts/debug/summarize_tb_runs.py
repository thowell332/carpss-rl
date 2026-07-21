
import argparse, glob, json, os, statistics
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

def moving_avg(xs, k):
    if k <= 1 or k > len(xs):
        return xs[:]
    out = []
    s = sum(xs[:k])
    out.append(s / k)
    for i in range(k, len(xs)):
        s += xs[i] - xs[i-k]
        out.append(s / k)
    pad = [out[0]] * (len(xs) - len(out))
    return pad + out

def linregress(y):
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

def pct_of_range(delta, lo, hi):
    r = max(1e-8, hi-lo)
    return 100.0 * abs(delta) / r

def summarize_event_file(path, ma_window=200):
    ea = EventAccumulator(path, size_guidance={"scalars": 0})
    ea.Reload()
    scalars = {t: ea.Scalars(t) for t in ea.Tags().get("scalars", [])}
    def extract(tag):
        if tag not in scalars or len(scalars[tag]) < 2:
            return None
        steps = [s.step for s in scalars[tag]]
        vals  = [float(s.value) for s in scalars[tag]]
        return steps, vals

    # reward tag selection
    reward_tag = None
    for candidate in ["eval/mean_reward", "rollout/ep_rew_mean"]:
        if candidate in scalars:
            reward_tag = candidate
            break

    reward_info = None
    if reward_tag:
        ev = extract(reward_tag)
        if ev:
            steps, vals = ev
            k = max(5, min(len(vals)//10, ma_window))
            mav = moving_avg(vals, k)
            tail = mav[int(len(mav)*0.8):] if len(mav)>=10 else mav
            slope, _ = linregress(tail)
            lo, hi = min(mav), max(mav)
            tail_delta_pct = pct_of_range(slope * len(tail), lo, hi)
            reward_info = {
                "tag": reward_tag,
                "n_points": len(vals),
                "last_step": steps[-1],
                "last_value": vals[-1],
                "tail_delta_pct_of_range": tail_delta_pct
            }

    # total timesteps if present
    total_ts = None
    if "time/total_timesteps" in scalars:
        ev = extract("time/total_timesteps")
        if ev:
            _, ts_vals = ev
            total_ts = int(ts_vals[-1])

    # td loss tail stats
    td_tag = "train/td_loss" if "train/td_loss" in scalars else ("train/loss" if "train/loss" in scalars else None)
    td_info = None
    if td_tag:
        ev = extract(td_tag)
        if ev:
            _, vals = ev
            tail = vals[int(len(vals)*0.8):] if len(vals)>=10 else vals
            var = statistics.pvariance(tail) if len(tail)>1 else 0.0
            td_info = {"tag": td_tag, "tail_points": len(tail), "tail_variance": var, "last_value": vals[-1]}

    return {
        "file": path,
        "reward": reward_info,
        "total_timesteps": total_ts,
        "td_loss": td_info,
        "sample_scalar_tags": sorted(list(scalars.keys()))[:10]
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--logdir", required=True)
    ap.add_argument("--ma_window", type=int, default=200)
    args = ap.parse_args()
    files = []
    for root, _, _ in os.walk(args.logdir):
        for p in glob.glob(os.path.join(root, "events.out.tfevents.*")):
            files.append(p)
    summaries = [summarize_event_file(f, ma_window=args.ma_window) for f in sorted(files)]
    print(json.dumps(summaries, indent=2))

if __name__ == "__main__":
    main()
