"""Iteration 18 — Synthetic mechanism test for graph-conditioned prediction.

Pre-declared design (see iteration18_results.md for full writeup):

CORPUS. Vocabulary of 200 tokens:
  - t00..t19: 20 topic markers
  - w00..w99: 100 topic-neutral filler words
  - s00..s79: 80 topic-specific words, 4 per topic (topic T owns
                s[T*4..T*4+3])

Each document: pick topic T uniformly, emit marker tT as word 0, then
emit 100 more words where each position is drawn from:
  - 40% topic marker tT
  - 30% uniform over the 4 topic-specific s words for T
  - 30% uniform over all 100 filler w words

The long-range signal: the 30% topic-specific emissions in positions
50..100 are conditionally dependent on the topic marker at position 0.
A local-context predictor (n-gram) can only catch this dependence by
accident — whenever a recent topic emission happens to sit in its
context window. A graph-conditioned predictor that tracks the
document-so-far bag of words can exploit the dependence directly.

PREDICTORS.
  1. N-gram backoff (Laplace). The A6 baseline inside the same harness.
  2. Graph-conditioned: word graph built from (co_doc) pairs during
     training. At prediction time, blend the n-gram score with a graph
     routing score computed from the document-so-far bag of words.
     Mixing exponent alpha swept over {0.0, 0.1, 0.25, 0.5, 0.75}. At
     alpha=0 the blended model must exactly match the n-gram baseline
     (pre-declared sanity check).

METRIC. Bits per word on 1000-doc eval slice, plus bits per character
(word length + 1 for separator) for direct comparison to iter 15 units.
Plus bits per word restricted to target positions whose true word is an
s word, since that is where the long-range signal actually lives.

SUCCESS CRITERION. Best alpha beats alpha=0 (n-gram) by >= 0.05 bits
per word total, OR by >= 0.20 bits per word on the s-word subset.
Either qualifies as a mechanism win. Neither is a clean negative.

Scope: single file, no edits to any live module. Seed 17.
"""

from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from pathlib import Path

# ---- Corpus ----

N_TOPICS = 20
N_FILLER = 100
S_PER_TOPIC = 4
DOC_LEN = 101  # marker + 100 body tokens
N_TRAIN_DOCS = 10_000
N_EVAL_DOCS = 1_000
SEED = 17


def build_vocab():
    topics = [f"t{i:02d}" for i in range(N_TOPICS)]
    fillers = [f"w{i:02d}" for i in range(N_FILLER)]
    specifics = [f"s{i:02d}" for i in range(N_TOPICS * S_PER_TOPIC)]
    return topics, fillers, specifics


def topic_s_words(t_idx, specifics):
    return specifics[t_idx * S_PER_TOPIC : (t_idx + 1) * S_PER_TOPIC]


def gen_doc(rng, topics, fillers, specifics):
    t_idx = rng.randrange(N_TOPICS)
    marker = topics[t_idx]
    s_pool = topic_s_words(t_idx, specifics)
    doc = [marker]
    for _ in range(DOC_LEN - 1):
        r = rng.random()
        if r < 0.40:
            doc.append(marker)
        elif r < 0.70:
            doc.append(s_pool[rng.randrange(S_PER_TOPIC)])
        else:
            doc.append(fillers[rng.randrange(N_FILLER)])
    return doc


def gen_corpus(n_docs, rng, topics, fillers, specifics):
    return [gen_doc(rng, topics, fillers, specifics) for _ in range(n_docs)]


# ---- N-gram model (Laplace-smoothed backoff, order 3) ----


class NGram:
    def __init__(self, vocab, order=3, alpha_smooth=0.1):
        self.vocab = vocab
        self.V = len(vocab)
        self.idx = {w: i for i, w in enumerate(vocab)}
        self.order = order
        self.alpha_smooth = alpha_smooth
        # counts[k] maps context tuple of length k to dict[word -> count]
        self.counts = [defaultdict(lambda: defaultdict(int)) for _ in range(order + 1)]
        self.totals = [defaultdict(int) for _ in range(order + 1)]

    def train(self, docs):
        for doc in docs:
            for i in range(len(doc)):
                w = doc[i]
                for k in range(self.order + 1):
                    ctx = tuple(doc[max(0, i - k) : i])
                    if len(ctx) != k:
                        continue
                    self.counts[k][ctx][w] += 1
                    self.totals[k][ctx] += 1

    def prob(self, word, history):
        """Simple backoff: try order k=self.order down to 0, pick the
        first context that exists and return Laplace-smoothed P(word|ctx).
        Always returns a non-zero value thanks to Laplace."""
        for k in range(self.order, -1, -1):
            ctx = tuple(history[-k:]) if k > 0 else ()
            if k > 0 and ctx not in self.counts[k]:
                continue
            c = self.counts[k][ctx].get(word, 0)
            t = self.totals[k][ctx]
            return (c + self.alpha_smooth) / (t + self.alpha_smooth * self.V)
        # Fallback (shouldn't hit since k=0 always exists once trained)
        return 1.0 / self.V

    def dist(self, history):
        """Full distribution over vocab for given history. Returns list
        of probabilities aligned with self.vocab."""
        out = [self.prob(w, history) for w in self.vocab]
        s = sum(out)
        return [x / s for x in out]


# ---- Graph model (co-document co-occurrence) ----


class CoDocGraph:
    def __init__(self, vocab):
        self.vocab = vocab
        # adj[word] = dict[other_word -> count of documents they co-occur in]
        self.adj = defaultdict(lambda: defaultdict(int))
        self.row_total = defaultdict(int)

    def train(self, docs):
        for doc in docs:
            types = set(doc)
            for a in types:
                for b in types:
                    if a == b:
                        continue
                    self.adj[a][b] += 1
            for a in types:
                self.row_total[a] += len(types) - 1

    def route_scores(self, bag):
        """Given bag = multiset of words seen so far in the current
        document, return dict[word -> unnormalized routing score]. Score
        is sum over w in bag of P(c | w) under the co-doc graph."""
        scores = defaultdict(float)
        for w, count in bag.items():
            row = self.adj.get(w)
            if not row:
                continue
            tot = self.row_total[w]
            if tot == 0:
                continue
            for c, v in row.items():
                scores[c] += count * (v / tot)
        return scores


# ---- Blended predictor ----


def blended_dist(ngram, graph, vocab, history, bag, alpha, eps=1e-6):
    ng = ngram.dist(history)
    if alpha == 0.0:
        return ng
    route = graph.route_scores(bag)
    # Align route scores to vocab order with eps smoothing.
    r = [route.get(w, 0.0) + eps for w in vocab]
    rs = sum(r)
    r = [x / rs for x in r]
    # log-linear mixture, then renormalize
    out = []
    for p_ng, p_r in zip(ng, r):
        out.append((p_ng ** (1 - alpha)) * (p_r ** alpha))
    s = sum(out)
    return [x / s for x in out]


# ---- Evaluation ----


def eval_bpw(ngram, graph, vocab, eval_docs, alpha):
    idx = {w: i for i, w in enumerate(vocab)}
    total_bits = 0.0
    total_words = 0
    total_chars = 0  # word length + 1 for separator
    s_bits = 0.0
    s_words = 0

    for doc in eval_docs:
        bag = defaultdict(int)
        # Start-of-doc: predict word 0 from empty history.
        for pos, w in enumerate(doc):
            history = doc[max(0, pos - ngram.order) : pos]
            dist = blended_dist(ngram, graph, vocab, history, bag, alpha)
            p = dist[idx[w]]
            bits = -math.log2(max(p, 1e-300))
            total_bits += bits
            total_words += 1
            total_chars += len(w) + 1
            if w.startswith("s"):
                s_bits += bits
                s_words += 1
            bag[w] += 1

    return {
        "alpha": alpha,
        "bpw": total_bits / total_words,
        "bpc": total_bits / total_chars,
        "s_bpw": (s_bits / s_words) if s_words else float("nan"),
        "s_words": s_words,
        "total_words": total_words,
    }


# ---- Main ----


def main():
    rng = random.Random(SEED)
    topics, fillers, specifics = build_vocab()
    vocab = topics + fillers + specifics
    print(f"vocab size: {len(vocab)} "
          f"({len(topics)} topics, {len(fillers)} filler, "
          f"{len(specifics)} s-words)")

    print(f"generating {N_TRAIN_DOCS} train docs, {N_EVAL_DOCS} eval docs "
          f"(doc_len={DOC_LEN}, seed={SEED})...")
    train_docs = gen_corpus(N_TRAIN_DOCS, rng, topics, fillers, specifics)
    eval_docs = gen_corpus(N_EVAL_DOCS, rng, topics, fillers, specifics)
    print(f"  train words: {sum(len(d) for d in train_docs):,}")
    print(f"  eval words:  {sum(len(d) for d in eval_docs):,}")

    print("training n-gram (order=3, Laplace alpha=0.1)...")
    ngram = NGram(vocab, order=3, alpha_smooth=0.1)
    ngram.train(train_docs)

    print("building co-doc graph...")
    graph = CoDocGraph(vocab)
    graph.train(train_docs)
    print(f"  graph rows: {len(graph.adj)}  "
          f"avg row len: "
          f"{(sum(len(v) for v in graph.adj.values()) / max(1, len(graph.adj))):.1f}")

    results = []
    for alpha in [0.0, 0.1, 0.25, 0.5, 0.75]:
        r = eval_bpw(ngram, graph, vocab, eval_docs, alpha)
        print(
            f"alpha={alpha:>5}  bpw={r['bpw']:.4f}  bpc={r['bpc']:.4f}  "
            f"s_bpw={r['s_bpw']:.4f}  (s_words={r['s_words']})"
        )
        results.append(r)

    baseline = next(r for r in results if r["alpha"] == 0.0)
    best = min(results, key=lambda r: r["bpw"])
    best_s = min(results, key=lambda r: r["s_bpw"])

    print()
    print(f"baseline (alpha=0):  bpw={baseline['bpw']:.4f}  "
          f"s_bpw={baseline['s_bpw']:.4f}")
    print(f"best total bpw:      alpha={best['alpha']}  "
          f"bpw={best['bpw']:.4f}  "
          f"delta={baseline['bpw'] - best['bpw']:+.4f}")
    print(f"best s-word bpw:     alpha={best_s['alpha']}  "
          f"s_bpw={best_s['s_bpw']:.4f}  "
          f"delta={baseline['s_bpw'] - best_s['s_bpw']:+.4f}")

    total_win = (baseline["bpw"] - best["bpw"]) >= 0.05
    s_win = (baseline["s_bpw"] - best_s["s_bpw"]) >= 0.20
    verdict = (
        "MECHANISM WIN" if (total_win or s_win) else "NO SIGNAL"
    )
    print(f"\npre-declared verdict: {verdict}  "
          f"(total_win={total_win}, s_word_win={s_win})")

    out_path = Path(__file__).parent / "iteration18_raw.json"
    out_path.write_text(json.dumps({
        "seed": SEED,
        "n_train_docs": N_TRAIN_DOCS,
        "n_eval_docs": N_EVAL_DOCS,
        "doc_len": DOC_LEN,
        "vocab_size": len(vocab),
        "results": results,
        "verdict": verdict,
        "total_win": total_win,
        "s_word_win": s_win,
    }, indent=2))
    print(f"[wrote {out_path}]")


if __name__ == "__main__":
    main()
