#!/usr/bin/env python3
"""
issu_schedule.py — Pianificazione rollout restart in background

Utilizzo:
  python3 issu_schedule.py --when-free --url http://IP:PORT/watching/state --deployment yt-flask --namespace kagent --manifest /desktop/flask-app/k8s/deployment.yaml
  python3 issu_schedule.py --at 14:30  --url http://IP:PORT/watching/state --deployment yt-flask --namespace kagent --manifest /desktop/flask-app/k8s/deployment.yaml
"""

import sys
import time
import subprocess
import urllib.request
import json
import argparse
from datetime import datetime, timedelta

POLL_INTERVAL = 2


def check_free(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
            return not data.get("watching", True)
    except Exception:
        return False


def wait_until_free(url: str):
    print(f"[{now()}] In attesa che il servizio si liberi...")
    while True:
        if check_free(url):
            print(f"[{now()}] Servizio libero.")
            return
        time.sleep(POLL_INTERVAL)


def wait_until_time(target: str):
    now_dt = datetime.now()
    target_dt = datetime.strptime(target, "%H:%M").replace(
        year=now_dt.year, month=now_dt.month, day=now_dt.day
    )
    if target_dt < now_dt:
        target_dt += timedelta(days=1)
    wait_sec = (target_dt - now_dt).total_seconds()
    print(f"[{now()}] Rilascio programmato alle {target}. Attendo {int(wait_sec)}s...")
    time.sleep(wait_sec)
    print(f"[{now()}] Orario raggiunto.")


def apply_manifest(manifest: str, namespace: str):
    print(f"[{now()}] Applicazione manifest {manifest}...")
    result = subprocess.run(
        ["kubectl", "apply", "-f", manifest, "-n", namespace],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"[{now()}] Manifest applicato con successo.")
    else:
        print(f"[{now()}] Errore apply manifest: {result.stderr}")
        sys.exit(1)


def rollout_restart(deployment: str, namespace: str):
    print(f"[{now()}] Avvio rollout restart di {deployment} in {namespace}...")
    result = subprocess.run(
        ["kubectl", "rollout", "restart", f"deployment/{deployment}", "-n", namespace],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"[{now()}] Rollout restart completato con successo.")
    else:
        print(f"[{now()}] Errore rollout restart: {result.stderr}")


def now():
    return datetime.now().strftime("%H:%M:%S")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--when-free", action="store_true")
    parser.add_argument("--at", type=str)
    parser.add_argument("--url", required=True)
    parser.add_argument("--deployment", required=True)
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    if args.at:
        wait_until_time(args.at)

    wait_until_free(args.url)
    apply_manifest(args.manifest, args.namespace)
    rollout_restart(args.deployment, args.namespace)


if __name__ == "__main__":
    main()
