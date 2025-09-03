#!/usr/bin/env python3
import subprocess
import os

def run_test(cmd):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("SUCCESS")
        print(result.stdout)
    else:
        print("FAILED")
        print(result.stderr)
    print("-" * 50)

# Test commands
commands = [
    "forge-tree validate structure.txt",
    "forge-tree forge structure.txt --verbose",
    "ls -la my-python-app/",
    "tree my-python-app/ || find my-python-app -type f"
]

for cmd in commands:
    run_test(cmd)
