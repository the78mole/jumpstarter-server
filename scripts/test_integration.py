#!/usr/bin/env python3
"""
Integration test for the Jumpstarter controller.

Verifies that:
1. The k3d cluster is reachable via kubectl.
2. All expected namespaces exist (cert-manager, traefik, jumpstarter).
3. All pods in those namespaces are Running or Completed.
4. The Jumpstarter controller gRPC endpoint is reachable on port 8082.

Exit code 0 = all tests passed.
Exit code non-zero = one or more tests failed.
"""

from __future__ import annotations

import subprocess
import sys
import time
import socket
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REQUIRED_NAMESPACES = ["cert-manager", "traefik", "jumpstarter"]
GRPC_HOST = "localhost"
GRPC_PORT = 8082
GRPC_TIMEOUT = 5  # seconds
MAX_WAIT_SECONDS = 120
POLL_INTERVAL = 5


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def run(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a subprocess command and return the result."""
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def kubectl(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return run(["kubectl", *args], check=check)


def passed(msg: str) -> None:
    print(f"  ✅  {msg}")


def failed(msg: str) -> None:
    print(f"  ❌  {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------


def test_cluster_reachable() -> bool:
    print("[1] Checking cluster reachability…")
    result = kubectl("cluster-info", check=False)
    if result.returncode == 0:
        passed("kubectl cluster-info succeeded")
        return True
    failed(f"kubectl cluster-info failed:\n{result.stderr.strip()}")
    return False


def test_namespaces_exist() -> bool:
    print("[2] Checking required namespaces…")
    result = kubectl("get", "namespaces", "-o", "jsonpath={.items[*].metadata.name}", check=False)
    if result.returncode != 0:
        failed(f"Could not list namespaces: {result.stderr.strip()}")
        return False

    existing: List[str] = result.stdout.split()
    all_ok = True
    for ns in REQUIRED_NAMESPACES:
        if ns in existing:
            passed(f"Namespace '{ns}' exists")
        else:
            failed(f"Namespace '{ns}' NOT found (found: {existing})")
            all_ok = False
    return all_ok


def test_pods_running(namespace: str) -> bool:
    """Return True if all pods in *namespace* are Running or Completed."""
    result = kubectl(
        "get", "pods", "-n", namespace,
        "-o", "jsonpath={range .items[*]}{.metadata.name}={.status.phase}\\n{end}",
        check=False,
    )
    if result.returncode != 0:
        failed(f"Could not list pods in '{namespace}': {result.stderr.strip()}")
        return False

    lines = [l for l in result.stdout.strip().splitlines() if l]
    if not lines:
        failed(f"No pods found in namespace '{namespace}'")
        return False

    all_ok = True
    for line in lines:
        name, _, phase = line.partition("=")
        if phase in ("Running", "Succeeded"):
            passed(f"  Pod {name!r} is {phase}")
        else:
            failed(f"  Pod {name!r} is in unexpected phase: {phase!r}")
            all_ok = False
    return all_ok


def test_all_pods_healthy() -> bool:
    print("[3] Checking pod health in required namespaces…")
    all_ok = True
    for ns in REQUIRED_NAMESPACES:
        print(f"    Namespace: {ns}")
        if not test_pods_running(ns):
            all_ok = False
    return all_ok


def _wait_for_pods(namespace: str) -> None:
    """Block until all pods in *namespace* are ready (best-effort)."""
    deadline = time.monotonic() + MAX_WAIT_SECONDS
    while time.monotonic() < deadline:
        result = kubectl(
            "get", "pods", "-n", namespace,
            "-o", "jsonpath={.items[*].status.containerStatuses[*].ready}",
            check=False,
        )
        statuses = result.stdout.split()
        if statuses and all(s == "true" for s in statuses):
            return
        time.sleep(POLL_INTERVAL)


def test_grpc_port_open() -> bool:
    print(f"[4] Checking gRPC port {GRPC_HOST}:{GRPC_PORT}…")
    _wait_for_pods("jumpstarter")
    try:
        with socket.create_connection((GRPC_HOST, GRPC_PORT), timeout=GRPC_TIMEOUT):
            passed(f"TCP connection to {GRPC_HOST}:{GRPC_PORT} succeeded")
            return True
    except (socket.timeout, ConnectionRefusedError, OSError) as exc:
        failed(f"Cannot reach {GRPC_HOST}:{GRPC_PORT} — {exc}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    print("=" * 60)
    print("  Jumpstarter-in-a-Box — Integration Tests")
    print("=" * 60)

    results: List[Tuple[str, bool]] = [
        ("Cluster reachable", test_cluster_reachable()),
        ("Namespaces exist", test_namespaces_exist()),
        ("Pods healthy", test_all_pods_healthy()),
        ("gRPC port open", test_grpc_port_open()),
    ]

    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    total_passed = sum(1 for _, ok in results if ok)
    total = len(results)
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}]  {name}")

    print(f"\n  {total_passed}/{total} tests passed")
    print("=" * 60)
    return 0 if total_passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
