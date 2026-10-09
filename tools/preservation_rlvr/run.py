"""Separate CLI for CTH-PRESERVATION-001; does not alter the inventory benchmark."""
import argparse
import hashlib
import json
import signal
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from tools.rlvr.providers import ProviderError, generate, budget_diagnostics
from tools.rlvr.run import model_spec, positive
from tools.rlvr.environment import ROOT
from .environment import DEFAULT_TASK, PreservationEnvironment
from .controls import oracle_answer, discover_and_read


@contextmanager
def deadline(seconds):
    if not hasattr(signal, 'setitimer'):
        raise ProviderError('HARD_DEADLINE_REQUIRES_POSIX')
    def expired(signum, frame):
        raise ProviderError('CLIENT_WALL_TIME_LIMIT')
    previous = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--self-test', action='store_true')
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--model', type=model_spec)
    parser.add_argument('--task', type=Path, default=DEFAULT_TASK)
    parser.add_argument('--output-dir', type=Path, default=ROOT/'output/rlvr/preservation')
    parser.add_argument('--reasoning-effort', choices=['low','medium','high'], default='low')
    parser.add_argument('--max-output-tokens', type=positive, default=8192)
    parser.add_argument('--episode-output-tokens', type=positive, default=98304)
    parser.add_argument('--timeout', type=positive, default=180)
    parser.add_argument('--wall-timeout', type=positive, default=300)
    parser.add_argument('--openrouter-key-file', type=Path)
    args = parser.parse_args(argv)
    if args.model and args.model[0] != 'openrouter':
        parser.error('This agent runner currently supports OpenRouter models only')
    env = PreservationEnvironment(args.task)
    public = env.reset()
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]
    destination = args.output_dir.resolve()/run_id
    destination.mkdir(parents=True, exist_ok=False)
    dump = lambda name, data: (destination/name).write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n')
    dump('observation.json', public)
    dump('run.json', {'run_id': run_id, 'task_id': env.task['task_id'], 'task_sha256': env.task_hash,
                     'source_count': len(env.documents), 'schema_sha256': env.task['schema_sha256'],
                     'policy_sha256': env.task['policy_sha256'], 'oracle_sha256': env.task['oracle_sha256'],
                     'harness_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')},
                     'model': args.model, 'reasoning_effort': args.reasoning_effort,
                     'max_output_tokens_per_request': args.max_output_tokens,
                     'episode_output_tokens': args.episode_output_tokens, 'socket_timeout': args.timeout,
                     'wall_timeout_per_request': args.wall_timeout,
                     'review_status': 'Development oracle; independent review and frontier calibration pending'})
    if args.dry_run:
        dump('result.json', {'kind': 'dry_run', 'api_calls': 0})
    elif args.self_test:
        answer = oracle_answer(env)
        trace = discover_and_read(env, answer)
        action = {'tool': 'submit', 'answer': answer}
        result = env.step(action); trace.append({'action': action, 'result': result})
        assert result['reward'] == 1 and result['success']
        dump('control_trace.json', trace)
        env.reset(); empty = env.step({'tool':'submit','answer':{'assessments':{}}})
        assert empty['reward'] == 0
        dump('result.json', {'kind': 'oracle_control_not_model_evaluation', 'positive': result, 'empty': empty, 'api_calls': 0})
    else:
        messages = [{'role':'user','content':json.dumps(public, ensure_ascii=False)}]
        total_tokens, total_cost, costs_known, calls = 0, 0.0, True, 0
        result = None
        with (destination/'trajectory.jsonl').open('w') as stream:
            while not env.done:
                remaining = args.episode_output_tokens-total_tokens
                if remaining <= 0:
                    result = env._finish('EPISODE_OUTPUT_TOKEN_LIMIT'); break
                cap = min(args.max_output_tokens, remaining)
                calls += 1
                start = time.monotonic(); record = {'call':calls,'requested_model':args.model[1]}
                try:
                    with deadline(args.wall_timeout):
                        reply = generate(*args.model, messages, max_tokens=cap, timeout=args.timeout,
                                         openrouter_key_file=args.openrouter_key_file,
                                         reasoning_effort=args.reasoning_effort)
                    record.update(reply)
                    record['budget_diagnostics'] = budget_diagnostics(reply, cap)
                    output = reply['tokens'].get('output')
                    if type(output) is not int or output < 0:
                        raise ProviderError('MISSING_USAGE_FOR_EPISODE_BUDGET')
                    total_tokens += output
                    cost = reply.get('cost_usd')
                    if cost is None:
                        costs_known = False
                    else:
                        total_cost += cost
                    if total_tokens > args.episode_output_tokens:
                        result = env._finish('EPISODE_OUTPUT_TOKEN_LIMIT')
                    else:
                        result = env.step(reply['completion'])
                    record['environment'] = result
                    messages.append({'role':'assistant','content':reply['completion']})
                    if not result['done']:
                        messages.append({'role':'user','content':json.dumps(result, ensure_ascii=False)})
                except ProviderError as error:
                    record['error_code'] = str(error)
                    result = {'done':True,'reward':None,'success':False,'failure_codes':[str(error)],'status':'request_error'}
                    env.done = True
                    costs_known = False
                record['latency_seconds'] = round(time.monotonic()-start,4)
                stream.write(json.dumps(record, ensure_ascii=False)+'\n');stream.flush()
                print('Call',record['call'], 'done' if result['done'] else 'tool step',flush=True)
        dump('result.json', {'kind':'model_episode','result':result,'calls':calls,'reported_output_tokens':total_tokens,
                            'reported_cost_usd':total_cost if costs_known else None,
                            'known_cost_subtotal_usd':total_cost,'steps':env.steps})
    print('Results:', destination)
    return 2 if args.model and result.get('reward') is None else 0


if __name__ == '__main__':
    raise SystemExit(main())
