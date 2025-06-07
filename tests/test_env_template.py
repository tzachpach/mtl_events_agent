import re
import os
import yaml
import pytest

def extract_env_keys_from_env_example(path=".env.example"):
    keys = set()
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                key = line.split('=', 1)[0].strip()
                if key:
                    keys.add(key)
    except FileNotFoundError:
        pytest.skip("File .env.example not found")
    return keys

def extract_env_keys_from_workflow(path=".github/workflows/publish.yml"):
    keys = set()
    with open(path) as f:
        content = f.read()
    # Find all ${{ secrets.KEY }} and ${{ env.KEY }}
    for match in re.findall(r'\$\{\{ ?(?:secrets|env)\.([A-Z0-9_]+) ?\}\}', content):
        keys.add(match)
    return keys

def test_env_template_matches_workflow():
    env_keys = extract_env_keys_from_env_example()
    workflow_keys = extract_env_keys_from_workflow()
    # Only check for required runtime envs, not build-time or action-only
    # Allow .env.example to have extras, but not to miss any workflow keys
    missing = workflow_keys - env_keys
    assert not missing, f"Missing in .env.example: {missing}" 