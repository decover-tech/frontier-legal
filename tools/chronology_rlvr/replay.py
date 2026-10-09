"""Replay recorded chronology actions locally, without provider calls or credentials."""
import argparse
import hashlib
import json
from pathlib import Path

from .environment import ChronologyEnvironment


def replay(path):
    archive = json.loads(Path(path).read_text())
    env = ChronologyEnvironment()
    if archive['task_sha256'] != env.task_hash:
        raise ValueError('Recorded task hash does not match this checkout')
    summary = []
    for model in archive['models']:
        public = env.reset()
        serialized = json.dumps(public, indent=2, ensure_ascii=False) + '\n'
        if hashlib.sha256(serialized.encode()).hexdigest() != model['observation_sha256']:
            raise ValueError('Initial observation changed for ' + model['model'])
        transitions = 0
        actual = None
        for response in model['responses']:
            expected = response.get('environment')
            if expected is None:
                continue
            if expected.get('failure_codes') == ['EPISODE_OUTPUT_TOKEN_LIMIT']:
                actual = env._finish('EPISODE_OUTPUT_TOKEN_LIMIT')
            else:
                actual = env.step(response['completion'])
            transitions += 1
            if actual != expected:
                raise ValueError(f"Replay mismatch: {model['model']}, transition {transitions}")
        if actual != model['final_result']:
            raise ValueError('Final result mismatch for ' + model['model'])
        summary.append({'model': model['model'], 'reward': actual['reward'],
                        'matched_transitions': transitions})
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args(argv)
    print(json.dumps({'models': replay(args.archive), 'api_calls': 0}, indent=2))


if __name__ == '__main__':
    main()
