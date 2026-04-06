# Iteration 15 — CLM vs nanoGPT on text8 (bpc)

All models evaluated on the same 5 MB held-out tail of text8 
(bytes 95,000,000 – 100,000,000). Lower is better.


| model | 1 MB | 10 MB | 50 MB | 90 MB |
|---|---|---|---|---|
| nanogpt_cpu | 2.5497 | 2.5150 | 2.5154 | 2.5176 |
| ppmd_o3 | 2.4891 | 2.3730 | 2.3465 | 2.3423 |
| ppmd_o5 | 2.2146 | 1.9101 | 1.8236 | 1.8044 |
| ppmd_o6 | 2.2377 | 1.8870 | 1.7621 | 1.7311 |

## Reference ceiling numbers (not reproduced here)

| model | bpc on text8 | source |
|---|---|---|
| Transformer-XL 24L | 1.08 | Dai et al. 2019 |
| small char-Transformer | ~1.3 | various |
| PPM-D historical | ~1.54 | Mahoney text8 benchmark |
| Shannon English estimate | ~1.3 | Shannon 1951 |

## Raw run data
```json
[
  {
    "model": "ppmd_o3",
    "train_mb": 1,
    "bpc": 2.4891229828729653,
    "eval_bytes": 500000,
    "train_time_s": 1.1661486625671387,
    "eval_time_s": 1.2397925853729248
  },
  {
    "model": "ppmd_o3",
    "train_mb": 10,
    "bpc": 2.3729579079759837,
    "eval_bytes": 500000,
    "train_time_s": 11.7782461643219,
    "eval_time_s": 1.2883291244506836
  },
  {
    "model": "ppmd_o3",
    "train_mb": 50,
    "bpc": 2.346483537916647,
    "eval_bytes": 500000,
    "train_time_s": 57.446412801742554,
    "eval_time_s": 1.2576026916503906
  },
  {
    "model": "ppmd_o3",
    "train_mb": 90,
    "bpc": 2.342289373373054,
    "eval_bytes": 500000,
    "train_time_s": 100.05073571205139,
    "eval_time_s": 1.3084349632263184
  },
  {
    "model": "ppmd_o5",
    "train_mb": 1,
    "bpc": 2.2145586621272115,
    "eval_bytes": 500000,
    "train_time_s": 2.0573086738586426,
    "eval_time_s": 1.380998134613037
  },
  {
    "model": "ppmd_o5",
    "train_mb": 10,
    "bpc": 1.9100948059013456,
    "eval_bytes": 500000,
    "train_time_s": 20.902263641357422,
    "eval_time_s": 1.2798407077789307
  },
  {
    "model": "ppmd_o5",
    "train_mb": 50,
    "bpc": 1.823592422918783,
    "eval_bytes": 500000,
    "train_time_s": 105.91297507286072,
    "eval_time_s": 1.2542500495910645
  },
  {
    "model": "ppmd_o5",
    "train_mb": 90,
    "bpc": 1.8043564653722786,
    "eval_bytes": 500000,
    "train_time_s": 183.42380619049072,
    "eval_time_s": 1.2345921993255615
  },
  {
    "model": "ppmd_o6",
    "train_mb": 1,
    "bpc": 2.237737811124794,
    "eval_bytes": 500000,
    "train_time_s": 2.8345131874084473,
    "eval_time_s": 1.498380184173584
  },
  {
    "model": "ppmd_o6",
    "train_mb": 10,
    "bpc": 1.8870401051832095,
    "eval_bytes": 500000,
    "train_time_s": 26.947035312652588,
    "eval_time_s": 1.3025989532470703
  },
  {
    "model": "ppmd_o6",
    "train_mb": 50,
    "bpc": 1.7620603883966457,
    "eval_bytes": 500000,
    "train_time_s": 126.035817861557,
    "eval_time_s": 1.2198143005371094
  },
  {
    "model": "ppmd_o6",
    "train_mb": 90,
    "bpc": 1.731069559664747,
    "eval_bytes": 500000,
    "train_time_s": 231.03738594055176,
    "eval_time_s": 1.343005657196045
  },
  {
    "model": "nanogpt_cpu",
    "train_mb": 1,
    "bpc": 2.5496720174658956,
    "eval_bytes": 496062,
    "train_time_s": 420.11261200904846,
    "train_steps": 2610,
    "final_train_loss": 1.5817437171936035,
    "n_params": 814592
  },
  {
    "model": "nanogpt_cpu",
    "train_mb": 10,
    "bpc": 2.5150465621742293,
    "eval_bytes": 496062,
    "train_time_s": 420.16310596466064,
    "train_steps": 2599,
    "final_train_loss": 1.7331547737121582,
    "n_params": 814592
  },
  {
    "model": "nanogpt_cpu",
    "train_mb": 50,
    "bpc": 2.515395350786676,
    "eval_bytes": 496062,
    "train_time_s": 420.10811948776245,
    "train_steps": 2575,
    "final_train_loss": 1.7301265001296997,
    "n_params": 814592
  },
  {
    "model": "nanogpt_cpu",
    "train_mb": 90,
    "bpc": 2.517569537820384,
    "eval_bytes": 496062,
    "train_time_s": 420.0716965198517,
    "train_steps": 2585,
    "final_train_loss": 1.7252932786941528,
    "n_params": 814592
  }
]
```
