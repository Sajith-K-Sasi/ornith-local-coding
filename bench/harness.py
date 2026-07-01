#!/usr/bin/env python3
"""Ornith local coding benchmark — quality harness.

Sends coding tasks to an OpenAI-compatible endpoint, extracts the generated
code, and runs it against hidden test cases in a sandboxed subprocess.

Lessons baked in (see ../README.md):
  * Use the model's recommended sampling + a fixed seed, NOT greedy decoding —
    greedy makes reasoning models loop.
  * Give a big enough max_tokens budget: reasoning (<think>) tokens count
    against it, so too-small a cap yields false failures.

Usage:
  python3 harness.py --base-url http://127.0.0.1:8080/v1 --model ornith \
      --label q4 --out results/q4.json
"""
import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
import time
import urllib.request

from tasks import TASKS


def chat(base, model, prompt, max_tokens, seed, temp, top_k, top_p):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temp,
        "top_k": top_k,
        "top_p": top_p,
        "seed": seed,
        "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=body, headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=1800) as r:
        d = json.load(r)
    wall = time.time() - t0
    ch = d["choices"][0]
    msg = ch["message"]
    return {
        "content": msg.get("content") or "",
        "reasoning": msg.get("reasoning_content") or "",
        "finish": ch.get("finish_reason"),
        "usage": d.get("usage", {}),
        "timings": d.get("timings", {}),
        "wall": wall,
    }


def extract_code(text):
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, re.DOTALL)
    return blocks[-1] if blocks else text


def run_tests(code, fn, cases):
    runner = textwrap.dedent(f"""
        import json, math, signal
        signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(TimeoutError()))
        signal.alarm(10)
        ns = {{}}
        try:
            exec(json.loads({json.dumps(json.dumps(code))}), ns)
        except Exception as e:
            print("IMPORTERR:" + repr(e)); raise SystemExit
        f = ns.get({json.dumps(fn)})
        if f is None:
            print("NOFUNC"); raise SystemExit
        cases = json.loads({json.dumps(json.dumps(cases))})
        passed = 0
        for inp, exp in cases:
            try:
                got = f(inp)
                ok = (math.isclose(got, exp, rel_tol=1e-9, abs_tol=1e-9)
                      if isinstance(exp, (int, float)) and isinstance(got, (int, float))
                      else got == exp)
                passed += 1 if ok else 0
            except Exception:
                pass
        print(f"RESULT:{{passed}}/{{len(cases)}}")
    """)
    try:
        p = subprocess.run([sys.executable, "-c", runner],
                           capture_output=True, text=True, timeout=20)
        m = re.search(r"RESULT:(\d+)/(\d+)", p.stdout)
        if m:
            return int(m.group(1)), int(m.group(2)), p.stdout.strip()
        return 0, len(cases), (p.stdout + p.stderr).strip()[:200]
    except subprocess.TimeoutExpired:
        return 0, len(cases), "HARNESS_TIMEOUT"


def main():
    ap = argparse.ArgumentParser(description="Ornith coding quality benchmark")
    ap.add_argument("--base-url", default="http://127.0.0.1:8080/v1")
    ap.add_argument("--model", default="ornith")
    ap.add_argument("--label", default="model")
    ap.add_argument("--out", default="results/quality.json")
    ap.add_argument("--max-tokens", type=int, default=16384)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--temp", type=float, default=0.6)
    ap.add_argument("--top-k", type=int, default=20)
    ap.add_argument("--top-p", type=float, default=0.95)
    args = ap.parse_args()

    out_dir = os.path.dirname(os.path.abspath(args.out)) or "."
    art = os.path.join(out_dir, "artifacts")
    os.makedirs(art, exist_ok=True)

    results = []
    for t in TASKS:
        r = chat(args.base_url, args.model, t["prompt"], args.max_tokens,
                 args.seed, args.temp, args.top_k, args.top_p)
        code = extract_code(r["content"])
        with open(os.path.join(art, f"{args.label}_{t['name']}.code.py"), "w") as f:
            f.write(code)
        with open(os.path.join(art, f"{args.label}_{t['name']}.reasoning.txt"), "w") as f:
            f.write(r["reasoning"])
        passed, total, note = run_tests(code, t["fn"], t["cases"])
        tim = r["timings"]
        results.append({
            "task": t["name"], "passed": passed, "total": total,
            "finish": r["finish"],
            "completion_tokens": r["usage"].get("completion_tokens"),
            "reasoning_chars": len(r["reasoning"]),
            "tg_tps": tim.get("predicted_per_second"),
            "wall_s": round(r["wall"], 1), "note": note,
        })
        print(f"[{args.label}] {t['name']}: {passed}/{total}  "
              f"gen={r['usage'].get('completion_tokens')}tok  "
              f"finish={r['finish']}  wall={r['wall']:.0f}s")

    summary = {
        "label": args.label,
        "total_passed": sum(x["passed"] for x in results),
        "total_cases": sum(x["total"] for x in results),
        "avg_tg_tps": round(sum((x["tg_tps"] or 0) for x in results) / len(results), 1),
        "total_wall_s": round(sum(x["wall_s"] for x in results), 1),
        "tasks": results,
    }
    os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[{args.label}] TOTAL {summary['total_passed']}/{summary['total_cases']} "
          f"| avg tg {summary['avg_tg_tps']} t/s "
          f"| {summary['total_wall_s']}s for all tasks | -> {args.out}")


if __name__ == "__main__":
    main()
