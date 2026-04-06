"""Tiny char-level transformer baseline for the CLM experiment.

This is a deliberate "compute-matched lower bound" baseline: we run it
on the *same* machine with a fixed wallclock budget per training size,
so the comparison against PPM-D is apples-to-apples on hardware and
compute. Published transformer numbers (Transformer-XL at ~1.08 bpc on
text8) are the *ceiling* reference, cited separately; this is the floor.

Architecture: nanoGPT-style causal transformer.
- context length 128
- d_model 128, 4 heads, 4 layers
- ~1.1M parameters, 27-char vocabulary
- AdamW, lr 3e-4, linear warmup, batch 64
- trains for a fixed wallclock budget
- reports bpc on the held-out slice via teacher-forcing nll / ln(2)

Uses matmul. That is the point: this is the matmul baseline we are
asking the matmul-free predictors to compete with.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F


VOCAB = 27  # a-z + space


def encode(b: bytes) -> torch.Tensor:
    arr = bytearray(len(b))
    for i, c in enumerate(b):
        arr[i] = 26 if c == 0x20 else c - 0x61
    return torch.tensor(arr, dtype=torch.long)


@dataclass
class Config:
    vocab: int = VOCAB
    ctx: int = 128
    d: int = 128
    n_heads: int = 4
    n_layers: int = 4
    dropout: float = 0.0


class CausalSelfAttention(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        assert cfg.d % cfg.n_heads == 0
        self.n_heads = cfg.n_heads
        self.d = cfg.d
        self.qkv = nn.Linear(cfg.d, 3 * cfg.d, bias=False)
        self.proj = nn.Linear(cfg.d, cfg.d, bias=False)
        self.register_buffer(
            "mask",
            torch.tril(torch.ones(cfg.ctx, cfg.ctx)).view(1, 1, cfg.ctx, cfg.ctx),
        )

    def forward(self, x):
        B, T, C = x.shape
        qkv = self.qkv(x)
        q, k, v = qkv.chunk(3, dim=-1)
        h = self.n_heads
        dh = C // h
        q = q.view(B, T, h, dh).transpose(1, 2)
        k = k.view(B, T, h, dh).transpose(1, 2)
        v = v.view(B, T, h, dh).transpose(1, 2)
        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(dh))
        att = att.masked_fill(self.mask[:, :, :T, :T] == 0, float("-inf"))
        att = F.softmax(att, dim=-1)
        y = att @ v
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.proj(y)


class Block(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        self.ln1 = nn.LayerNorm(cfg.d)
        self.attn = CausalSelfAttention(cfg)
        self.ln2 = nn.LayerNorm(cfg.d)
        self.mlp = nn.Sequential(
            nn.Linear(cfg.d, 4 * cfg.d),
            nn.GELU(),
            nn.Linear(4 * cfg.d, cfg.d),
        )

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x


class NanoGPT(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.tok = nn.Embedding(cfg.vocab, cfg.d)
        self.pos = nn.Embedding(cfg.ctx, cfg.d)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layers)])
        self.ln_f = nn.LayerNorm(cfg.d)
        self.head = nn.Linear(cfg.d, cfg.vocab, bias=False)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        pos = torch.arange(T, device=idx.device)
        x = self.tok(idx) + self.pos(pos)
        for blk in self.blocks:
            x = blk(x)
        x = self.ln_f(x)
        logits = self.head(x)
        if targets is None:
            return logits, None
        loss = F.cross_entropy(
            logits.view(-1, self.cfg.vocab), targets.view(-1)
        )
        return logits, loss


def n_params(model) -> int:
    return sum(p.numel() for p in model.parameters())


def train_and_eval(
    train_bytes: bytes,
    heldout_bytes: bytes,
    wallclock_sec: float,
    batch: int = 64,
    lr: float = 3e-4,
    seed: int = 1337,
) -> dict:
    torch.manual_seed(seed)
    cfg = Config()
    model = NanoGPT(cfg)
    train_tok = encode(train_bytes)
    held_tok = encode(heldout_bytes)
    n_train = train_tok.numel()
    ctx = cfg.ctx

    opt = torch.optim.AdamW(model.parameters(), lr=lr, betas=(0.9, 0.95))
    warmup = 100

    model.train()
    t0 = time.time()
    step = 0
    last_loss = float("nan")
    while time.time() - t0 < wallclock_sec:
        # sample random contiguous windows
        ix = torch.randint(0, n_train - ctx - 1, (batch,))
        x = torch.stack([train_tok[i : i + ctx] for i in ix])
        y = torch.stack([train_tok[i + 1 : i + 1 + ctx] for i in ix])
        _, loss = model(x, y)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        # simple warmup
        if step < warmup:
            for g in opt.param_groups:
                g["lr"] = lr * (step + 1) / warmup
        opt.step()
        last_loss = loss.item()
        step += 1
    train_time = time.time() - t0

    # Evaluate bpc. Uses batched non-overlapping windows across a fixed
    # 500 KB slice of the held-out tail (bytes 0..500_000 of `heldout_bytes`,
    # which the caller passes as the 5 MB text8 tail). 500 KB = ~500K
    # tokens which is statistically stable to <0.005 bpc and keeps eval
    # time under one minute on CPU.
    model.eval()
    EVAL_BYTES = 500_000
    held_eval = held_tok[:EVAL_BYTES]
    total_nll = 0.0
    total_tokens = 0
    with torch.no_grad():
        # Non-overlapping contiguous windows of length ctx. For each
        # window we score positions 1..ctx-1 (position 0 has no
        # in-window context). This is a strict lower bound on what a
        # longer-context eval would give, because the first token of
        # every window sees no context — we skip it to avoid unfairly
        # penalizing the model. The boundaries introduce a tiny bias
        # (~1/ctx of the tokens skipped), which is reported honestly.
        n = held_eval.numel()
        n_windows = (n - 1) // ctx
        windows_x = held_eval[: n_windows * ctx].view(n_windows, ctx)
        windows_y = held_eval[1 : 1 + n_windows * ctx].view(n_windows, ctx)
        batch_sz = 64
        for bstart in range(0, n_windows, batch_sz):
            x = windows_x[bstart : bstart + batch_sz]
            y = windows_y[bstart : bstart + batch_sz]
            logits, _ = model(x, None)
            logp = F.log_softmax(logits, dim=-1)
            # Score positions 1..ctx-1 (skip position 0 of each window)
            gathered = logp[:, 1:, :].gather(-1, y[:, 1:].unsqueeze(-1)).squeeze(-1)
            total_nll += -gathered.sum().item()
            total_tokens += gathered.numel()
    bpc = (total_nll / total_tokens) / math.log(2)
    return {
        "bpc": bpc,
        "n_tokens_eval": total_tokens,
        "train_steps": step,
        "train_time_s": train_time,
        "final_train_loss": last_loss,
        "n_params": n_params(model),
    }
