#!/usr/bin/env python3
"""
issu_check.py - Controlla se il servizio e libero o occupato.

Utilizzo:
  python3 issu_check.py --url http://192.168.49.2:32000/watching/state

Output:
  ISSU_FREE
  ISSU_OCCUPIED
"""

import subprocess
import json
import sys
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    args = parser.parse_args()

    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "5", args.url],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print("ISSU_OCCUPIED")
            sys.exit(0)

        data = json.loads(result.stdout)
        if data.get("watching", True) is False:
            print("ISSU_FREE")
        else:
            print("ISSU_OCCUPIED")
    except Exception:
        print("ISSU_OCCUPIED")


if __name__ == "__main__":
    main()
