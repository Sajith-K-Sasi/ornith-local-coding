# Ornith benchmarks

Reproduce the speed + quality numbers from the [top-level README](../README.md).
Measured on an M5 MacBook Air (24 GB), llama.cpp Metal backend.

## Speed

`llama-bench` measures prompt-processing and generation throughput directly from a gguf:

```bash
llama-bench -m /path/to/ornith-1.0-9b-Q4_K_M.gguf -ngl 99 -fa 1 -p 512,2048 -n 128
```

## Quality

`harness.py` sends the coding tasks in `tasks.py` to a **running** OpenAI-compatible
server, extracts the generated code, and runs it against hidden tests in a sandbox.

1. Serve the model (see [`../start_ornith.sh`](../start_ornith.sh)) so it's live at
   `http://127.0.0.1:8080/v1`.
2. Run it:

```bash
python3 harness.py --base-url http://127.0.0.1:8080/v1 --model ornith --label q4 --out results/q4.json
```

Pass counts + timings land in `results/`; the model's generated code and reasoning
traces land in `results/artifacts/` for inspection.

Or do both at once (loads the model twice — only on enough RAM):

```bash
./run_bench.sh /path/to/ornith-1.0-9b-Q4_K_M.gguf q4
```

## Two gotchas baked into the harness

1. **Don't use greedy decoding.** `temperature=0` makes reasoning models loop and never
   answer. The harness defaults to the recommended sampling (`temp 0.6, top-k 20, top-p 0.95`)
   with a fixed seed (`42`) — reproducible *and* not degenerate.
2. **Give a big token budget.** `<think>` tokens count against `max_tokens`; too small a cap
   gets eaten by reasoning before the answer, producing false failures. Default is `16384`.

Override any of it: `--temp`, `--seed`, `--max-tokens`, `--top-k`, `--top-p`.

## Our results (Ornith-9B)

| Task | Q4_K_M | Q6_K |
|---|---|---|
| merge_intervals | 7/7 | 7/7 |
| roman_to_int | 8/8 | 8/8 |
| calc | 0/8 | 0/8 |
| **Total** | **15/23** | **15/23** |

Wall-clock to finish all three tasks: **Q4 ~90 s**, Q6 ~5.5 min. Same quality, and Q4 is
~30% faster to generate — so Q4_K_M is the pick on 24 GB. (The 35B MoE at Q3 took ~16 min
for the same three: great burst speed, but it over-reasons.)
(`calc` fails on both: the model writes a subtly buggy parser — a capability limit, not a
precision one, so more bits don't fix it.)

## Add your own tasks

Append to `TASKS` in `tasks.py`: a `name`, the `fn` the model must define, a `prompt`, and
`cases` as `(input, expected)` pairs. The input is passed as the function's single argument.
