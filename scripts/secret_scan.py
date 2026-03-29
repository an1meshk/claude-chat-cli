#!/usr/bin/env python3
"""Lightweight secret scanner for repository files."""

import re
import subprocess
import sys

PATTERNS = {
    "Anthropic API Key": re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}", re.IGNORECASE),
    "Generic API Key": re.compile(r'(?:api[_\- ]?key|secret|token)[\"\']?\s*[:=]\s*[\"\'][A-Za-z0-9_\-]{16,}[\"\']', re.IGNORECASE),
    "SSH Private Key": re.compile(r"-----BEGIN OPENSSH PRIVATE KEY-----"),
    "RSA Private Key": re.compile(r"-----BEGIN RSA PRIVATE KEY-----"),
}


def get_tracked_files():
    output = subprocess.check_output(["git", "ls-files"]).decode("utf-8", errors="ignore")
    return [line.strip() for line in output.splitlines() if line.strip()]


def scan_file(path):
    secrets = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for lineno, line in enumerate(f, start=1):
                for name, pattern in PATTERNS.items():
                    if pattern.search(line):
                        secrets.append((path, lineno, name, line.strip()))
    except OSError:
        pass
    return secrets


def main():
    tracked_files = get_tracked_files()
    found = []

    for path in tracked_files:
        found.extend(scan_file(path))

    if found:
        print("Potential secrets detected:")
        for path, lineno, kind, snippet in found:
            print(f"{path}:{lineno} [{kind}] {snippet}")
        print("\nERROR: Please remove or rotate secrets and try again.")
        sys.exit(1)

    print("OK: No secrets detected in tracked files.")
    sys.exit(0)


if __name__ == "__main__":
    main()
