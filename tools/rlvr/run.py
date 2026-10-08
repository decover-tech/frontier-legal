"""CLI: python3 -m tools.rlvr.run --help (from repository root)."""
import argparse
import json
import statistics
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .environment import DEFAULT_TASK, ROOT, DateEnvironment, sha256, verify
from .providers import KEYS, ProviderError, generate, request_spec


def positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("Must be positive")
    return number


def model_spec(value):
    provider, separator, model = value.partition(":")
    if not separator or provider not in KEYS or not model.strip():
        raise argparse.ArgumentTypeError("Use openai:MODEL, anthropic:MODEL, or gemini:MODEL")
    return provider, model


def provenance():
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = None
    return {"repository_commit": commit, "harness_hashes": {
        p.name: sha256(p.read_bytes()) for p in sorted(Path(__file__).parent.glob("*.py"))}}


def summarize(records):
    result = []
    for provider, model in sorted({(r["provider"], r["requested_model"]) for r in records}):
        rows = [r for r in records if (r["provider"], r["requested_model"]) == (provider, model)]
        scored = [r for r in rows if r["status"] == "scored"]
        result.append({
            "provider": provider, "model": model, "attempts": len(rows),
            "scored": len(scored), "errors": len(rows) - len(scored),
            "mean_reward": statistics.mean(r["evaluation"]["reward"] for r in scored) if scored else None,
            "success_rate": statistics.mean(int(r["evaluation"]["success"]) for r in scored) if scored else None,
            "mean_latency_seconds": statistics.mean(r["latency_seconds"] for r in scored) if scored else None,
            "input_tokens": sum(r["tokens"]["input"] for r in scored) if scored and all(r["tokens"]["input"] is not None for r in scored) else None,
            "output_tokens": sum(r["tokens"]["output"] for r in scored) if scored and all(r["tokens"]["output"] is not None for r in scored) else None,
            "cost_usd": None,
        })
    return result


def self_test(env):
    observation = env.reset()
    # Evaluator-only deterministic baseline, explicitly not a model score.
    expected = env._expected
    cases = {
        "correct": json.dumps({"sent_date": expected}),
        "wrong_date": '{"sent_date":"1900-01-01"}',
        "malformed": "not JSON",
        "extra_field": json.dumps({"sent_date": expected, "explanation": "extra"}),
        "duplicate_key": '{"sent_date":"1900-01-01","sent_date":' + json.dumps(expected) + '}',
    }
    checks = {name: verify(answer, expected) for name, answer in cases.items()}
    assert checks["correct"]["reward"] == 1
    assert all(value["reward"] == 0 for name, value in checks.items() if name != "correct")
    return {"kind": "verifier_self_test_not_model_evaluation", "task_id": observation["task_id"], "checks": checks}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", type=Path, default=DEFAULT_TASK)
    parser.add_argument("--model", action="append", type=model_spec, default=[], help="Repeat for a model comparison")
    parser.add_argument("--repetitions", type=positive, default=1)
    parser.add_argument("--max-output-tokens", type=positive, default=1024)
    parser.add_argument("--timeout", type=positive, default=45)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output/rlvr")
    parser.add_argument("--self-test", action="store_true", help="Offline control test; no API calls")
    parser.add_argument("--dry-run", action="store_true", help="Validate task and save observation; no API calls")
    args = parser.parse_args(argv)
    if args.self_test and args.dry_run:
        parser.error("Choose --self-test or --dry-run")
    if not args.model and not (args.self_test or args.dry_run):
        parser.error("Supply --model or use --self-test / --dry-run")
    env = DateEnvironment(args.task)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    destination = args.output_dir.resolve() / run_id
    destination.mkdir(parents=True, exist_ok=False)
    observation = env.reset()
    (destination / "observation.json").write_text(json.dumps(observation, indent=2) + "\n")
    metadata = {
        "run_id": run_id, "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "task": env.task, "task_sha256": env.task_hash,
        "output_schema_sha256": sha256((ROOT / env.task["output_schema"]).read_bytes()),
        "configuration": {"models": args.model, "repetitions": args.repetitions,
                          "max_output_tokens": args.max_output_tokens, "timeout": args.timeout,
                          "reasoning_settings": "provider defaults; not equivalent across models",
                          "sampling_settings": "provider defaults; no seed guarantee"},
        **provenance(),
    }
    (destination / "run.json").write_text(json.dumps(metadata, indent=2) + "\n")
    if args.self_test:
        report = self_test(env)
        (destination / "self_test.json").write_text(json.dumps(report, indent=2) + "\n")
        print("Offline verifier controls passed (not a model evaluation).")
    elif args.dry_run:
        print("Validated task and evidence; saved public observation. No API calls.")
    else:
        records = []
        with (destination / "records.jsonl").open("w") as stream:
            for repetition in range(args.repetitions):
                for provider, model in args.model:
                    public = env.reset()
                    endpoint, body = request_spec(provider, model, public["messages"], args.max_output_tokens)
                    record = {"task_id": env.task["task_id"], "trial": repetition + 1,
                              "provider": provider, "requested_model": model,
                              "request": {"endpoint": endpoint, "body": body},
                              "status": "error", "evaluation": None, "cost_usd": None}
                    start = time.monotonic()
                    try:
                        record.update(generate(provider, model, public["messages"], args.max_output_tokens, args.timeout))
                        record["evaluation"] = env.step(record["completion"])
                        record["status"] = "scored"
                    except ProviderError as error:
                        record["error_code"] = str(error)
                    record["latency_seconds"] = round(time.monotonic() - start, 4)
                    records.append(record)
                    stream.write(json.dumps(record) + "\n")
                    stream.flush()
                    score = record["evaluation"]["reward"] if record["evaluation"] else record["error_code"]
                    print(f"{provider}:{model} trial {repetition + 1}: {score}", flush=True)
        summary = {"kind": "model_evaluation", "run_id": run_id, "task_id": env.task["task_id"],
                   "results": summarize(records),
                   "notes": ["Errors excluded from reward denominators and counted separately.",
                             "Costs unavailable; null is not zero.",
                             "One-email smoke test, not a frontier capability ranking."]}
        (destination / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        if any(r["status"] == "error" for r in records):
            print("Results:", destination)
            return 2
    print("Results:", destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
