"""Iteration 15 driver: run PPM-D and nanoGPT on text8 at 4 train sizes.

Produces:
  experiments/clm/iter15_results.json   — raw numbers
  experiments/clm/iter15_results.md     — human-readable table

All predictors evaluated on the same 5 MB held-out tail of text8.

Hypothesis: a matmul-free PPM-D predictor can produce a bpc curve on
text8 whose gap to a compute-matched CPU transformer baseline either
shrinks, stays flat, or widens as training data grows, and the shape
of that gap tells us whether pure surface-statistics compression has
a ceiling worth investing past.

Success criterion (live signal): PPM-D within 1.5x of the compute-
matched transformer bpc at 90 MB and the gap shrinking or flat with
scale.

Clean negative: PPM-D gap >2x and widening with scale.

This iteration does NOT include CTW (deferred to iter 16 pending this
curve). It also does NOT compare against published frontier transformer
numbers on our hardware; those are cited separately as a ceiling.
"""
from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from splits import splits  # noqa: E402
from ppmd import PPMD  # noqa: E402
from nano_gpt import train_and_eval  # noqa: E402

PPM_ORDERS = [3, 5, 6]
GPT_WALLCLOCK_S = 20 * 60  # 20 minutes per size


def run_ppm(trains: dict, heldout: bytes) -> list[dict]:
    rows = []
    for order in PPM_ORDERS:
        for mb, train_bytes in trains.items():
            print(f"[PPM-D order={order} train={mb}MB] starting", flush=True)
            t0 = time.time()
            model = PPMD(max_order=order)
            model.train(train_bytes)
            t_train = time.time() - t0
            t0 = time.time()
            bpc, n = model.eval_bpc(heldout)
            t_eval = time.time() - t0
            print(
                f"[PPM-D order={order} train={mb}MB] "
                f"bpc={bpc:.4f}  train={t_train:.0f}s  eval={t_eval:.0f}s",
                flush=True,
            )
            rows.append({
                "model": f"ppmd_o{order}",
                "train_mb": mb,
                "bpc": bpc,
                "eval_bytes": n,
                "train_time_s": t_train,
                "eval_time_s": t_eval,
            })
            # Free memory before next run
            del model
    return rows


def run_gpt(trains: dict, heldout: bytes) -> list[dict]:
    rows = []
    for mb, train_bytes in trains.items():
        print(f"[nanoGPT train={mb}MB] starting, budget={GPT_WALLCLOCK_S}s", flush=True)
        t0 = time.time()
        r = train_and_eval(
            train_bytes, heldout, wallclock_sec=GPT_WALLCLOCK_S
        )
        print(
            f"[nanoGPT train={mb}MB] bpc={r['bpc']:.4f} "
            f"steps={r['train_steps']} "
            f"final_train_loss={r['final_train_loss']:.3f} "
            f"wallclock={time.time()-t0:.0f}s",
            flush=True,
        )
        rows.append({
            "model": "nanogpt_cpu",
            "train_mb": mb,
            "bpc": r["bpc"],
            "eval_bytes": r["n_tokens_eval"],
            "train_time_s": r["train_time_s"],
            "train_steps": r["train_steps"],
            "final_train_loss": r["final_train_loss"],
            "n_params": r["n_params"],
        })
    return rows


def write_markdown(rows: list[dict], path: str) -> None:
    # Organize by model -> {train_mb: bpc}
    by_model: dict[str, dict[int, float]] = {}
    for r in rows:
        by_model.setdefault(r["model"], {})[r["train_mb"]] = r["bpc"]
    sizes = sorted({r["train_mb"] for r in rows})

    lines = []
    lines.append("# Iteration 15 — CLM vs nanoGPT on text8 (bpc)\n")
    lines.append("All models evaluated on the same 5 MB held-out tail of text8 ")
    lines.append("(bytes 95,000,000 – 100,000,000). Lower is better.\n\n")
    header = "| model | " + " | ".join(f"{s} MB" for s in sizes) + " |"
    sep = "|---|" + "---|" * len(sizes)
    lines.append(header)
    lines.append(sep)
    for model in sorted(by_model.keys()):
        row = [model] + [
            f"{by_model[model].get(s, float('nan')):.4f}" for s in sizes
        ]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("\n## Reference ceiling numbers (not reproduced here)\n")
    lines.append("| model | bpc on text8 | source |")
    lines.append("|---|---|---|")
    lines.append("| Transformer-XL 24L | 1.08 | Dai et al. 2019 |")
    lines.append("| small char-Transformer | ~1.3 | various |")
    lines.append("| PPM-D historical | ~1.54 | Mahoney text8 benchmark |")
    lines.append("| Shannon English estimate | ~1.3 | Shannon 1951 |")
    lines.append("\n## Raw run data")
    lines.append("```json")
    lines.append(json.dumps(rows, indent=2))
    lines.append("```\n")
    with open(path, "w") as f:
        f.write("\n".join(lines))


def main():
    trains, heldout = splits()
    print(f"heldout: {len(heldout):,} bytes, sizes: {list(trains)} MB", flush=True)
    all_rows = []
    print("\n=== PPM-D runs ===\n", flush=True)
    all_rows.extend(run_ppm(trains, heldout))
    print("\n=== nanoGPT runs ===\n", flush=True)
    all_rows.extend(run_gpt(trains, heldout))

    out_json = os.path.join(HERE, "iter15_results.json")
    out_md = os.path.join(HERE, "iter15_results.md")
    with open(out_json, "w") as f:
        json.dump(all_rows, f, indent=2)
    write_markdown(all_rows, out_md)
    print(f"\nwrote {out_json}\nwrote {out_md}", flush=True)


if __name__ == "__main__":
    main()
