# Ornith Local Coding

**Run [Ornith-1.0-9B](https://ornith.site/) — an agentic coding model — entirely on your laptop.** No API keys, no cloud bill, no code leaving your machine.

This repo is the exact setup + benchmarks behind running Ornith locally on a **fanless M5 MacBook Air (24 GB)** with [llama.cpp](https://github.com/ggml-org/llama.cpp) and the [pi](https://pi.dev) coding agent.

> TL;DR — On 24 GB the winning config is Ornith-9B **`Q4_K_M`**: same task quality as the near-lossless quants in testing, ~30% faster, ~5 GB, with local image understanding. See [the benchmarks](#benchmarks).

---

## Why local?

- **Private** — your code (and your screenshots) never leave the machine.
- **Free** — zero cost per token after a ~5 GB download.
- **Offline** — works on a plane, on bad WiFi, inside locked-down networks.
- **Yours** — MIT-licensed weights that don't get deprecated or repriced.

## What Ornith can do here

- **Agentic coding** — tool use, terminal work, multi-step reasoning (not just autocomplete).
- **Image understanding (local)** — with the vision encoder enabled, hand it a screenshot of a stack trace, a broken UI, or a diagram. The image is processed on-device and never uploaded.

---

## See it in action

Two real Ornith sessions from this setup — a 9B model, on a fanless MacBook Air, offline:

- **Built a game, then debugged it.** From the prompt *"create a playable brick breaker game,"* Ornith wrote a complete single-file HTML5 canvas game — paddle, angle-aware ball, 6×10 bricks, particle effects, lives, progressive levels. When told *"fix the level bug and the game-over bug,"* it identified both root causes and patched them.
  **▶ Play it: [brick-breaker.sajithk.in](https://brick-breaker.sajithk.in)** — source in [`examples/brick-breaker.html`](examples/brick-breaker.html).
- **Did live product research.** Asked for *"the cheapest 1080p, good-lumens projector under ₹25,000,"* Ornith drove a headed browser via pi, hit a Google CAPTCHA, **adapted to Amazon.in on its own**, and returned a comparison table of real listings with prices, lumens, and ratings.

---

## Quickstart

```bash
# 1. install llama.cpp (provides llama-server + llama-bench)
brew install llama.cpp

# 2. serve Ornith-9B Q4_K_M (first run downloads ~5 GB)
./run-ornith.sh
# -> OpenAI-compatible endpoint at http://127.0.0.1:8080/v1
```

Point any OpenAI-compatible client at `http://127.0.0.1:8080/v1`. For the **pi** agent, copy `models.json` into your pi config (it defines the `ornith` model on that endpoint).

### Enable image understanding (optional)

Download the vision encoder (`mmproj`) from the [Ornith GGUF repo](https://huggingface.co/deepreinforce-ai/Ornith-1.0-9B-GGUF), then:

```bash
export ORNITH_MMPROJ=/path/to/ornith-mmproj-f16.gguf
./run-ornith.sh
```

### Apple Silicon tip

The GPU can only wire a fraction of unified memory by default. For headroom (and required if you try bigger models):

```bash
sudo sysctl iogpu.wired_limit_mb=21000   # resets on reboot
```

---

## Benchmarks

Reproduce everything with [`bench/`](bench/). Measured on an M5 MacBook Air (24 GB), llama.cpp Metal backend.

### Speed (`llama-bench`, tokens/sec)

| Model | Size | prompt (pp512) | generate (tg128) |
|---|---|---|---|
| **9B Q4_K_M** | 5.2 GB | 526 | **22.3** |
| 9B Q6_K | 6.9 GB | 474 | 16.8 |
| 35B Q3 (MoE) | 15 GB | 722 | 40.5 *(burst)* |

Handy rule for this hardware: **`tokens/sec ≈ 115 ÷ model_size_GB`** (generation is memory-bandwidth bound). Fewer bits → directly faster.

### Quality (3 coding tasks, scored vs hidden tests)

| Task | 9B Q4 | 9B Q6 | 35B Q3 |
|---|---|---|---|
| `merge_intervals` | ✅ 7/7 | ✅ 7/7 | ✅ 7/7 |
| `roman_to_int` | ✅ 8/8 | ✅ 8/8 | ✅ 8/8 |
| `calc` (expr evaluator) | ❌ 0/8 | ❌ 0/8 | ❌ 0/8 |
| **Total** | **15/23** | **15/23** | **15/23** |

**Wall-clock to finish all 3 tasks:** 9B Q4 **~90 s** · 9B Q6 ~5.5 min · 35B Q3 **~16 min** (it over-reasons — 10k+ tokens to merge intervals).

**Takeaways:**
- Q4 = Q6 on quality → pick Q4 for the speed. The quality ladder saturates below Q6.
- `calc` fails on all: the 9B writes a subtly buggy parser (a capability limit, not precision — more bits won't fix it); the 35B *over-reasons* at Q3 and never commits to an answer within budget.
- The 35B MoE has great burst speed but at the only quant that fits 24 GB it over-thinks (10K+ tokens on a trivial task), so the **9B Q4 is the sweet spot** on this hardware. For the genuinely hard tasks, reach for a cloud model.

---

## Notes from benchmarking reasoning models (read before you trust your own numbers)

Two bugs produced *fake* failures in our first runs:

1. **Greedy decoding breaks reasoning models.** `temperature=0` sent the model into reasoning loops. Fix: use the recommended sampling (temp 0.6, top-k 20, top-p 0.95) with a **fixed seed** for reproducibility.
2. **`<think>` tokens count against `max_tokens`.** A too-small budget gets consumed by reasoning before the answer, yielding false 0-scores. Fix: a generous cap (16K here). The harness in this repo bakes both fixes in.

When a reasoning model "fails," check whether it actually *finished* before blaming the weights.

---

## Layout

```
start_ornith.sh   # serve Ornith on llama.cpp (Q4_K_M + optional vision)
run-ornith.sh     # one-command: dependency check -> serve
models.json       # pi agent provider block (points at the local endpoint)
bench/            # reproducible speed + quality benchmarks
```

## Links

- Ornith — https://ornith.site/
- Ornith-1.0-9B GGUF — https://huggingface.co/deepreinforce-ai/Ornith-1.0-9B-GGUF
- pi (the coding agent) — https://pi.dev
- llama.cpp — https://github.com/ggml-org/llama.cpp

## License

MIT — see [LICENSE](LICENSE).
