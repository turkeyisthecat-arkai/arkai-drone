#!/usr/bin/env python3
"""ARKAI local command-aware agent.

This module provides a simple local agent loop that keeps runtime state in
`runtime/state.json` while processing tasks and commands.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import threading
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional


BASE_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = BASE_DIR / "runtime"
STATE_PATH = RUNTIME_DIR / "state.json"


class ArkaiAgent:
    """A local agent with heartbeat, task processing, and command handling."""

    def __init__(self, heartbeat_interval: float = 2.0) -> None:
        self.heartbeat_interval = heartbeat_interval
        self.tasks: Deque[Dict[str, Any]] = deque()
        self.processed: List[Dict[str, Any]] = []
        self.failed: List[Dict[str, Any]] = []
        self.results: List[Dict[str, Any]] = []
        self.memory: Dict[str, Any] = {
            "agent": "arkai-local-agent",
            "version": "1.0",
            "started_at": self._now_iso(),
            "notes": [],
        }
        self.last_heartbeat: str = self._now_iso()

        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        self._ensure_runtime_state_file()
        self._write_state()

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _ensure_runtime_state_file(self) -> None:
        RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        if not STATE_PATH.exists():
            STATE_PATH.write_text("{}\n", encoding="utf-8")

    def _state_snapshot(self) -> Dict[str, Any]:
        return {
            "heartbeat": self.last_heartbeat,
            "tasks": list(self.tasks),
            "processed": self.processed,
            "failed": self.failed,
            "results": self.results,
            "memory": self.memory,
        }

    def _write_state(self) -> None:
        snapshot = self._state_snapshot()
        tmp_path = STATE_PATH.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp_path, STATE_PATH)

    def add_task(self, kind: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        task = {
            "id": str(uuid.uuid4()),
            "kind": kind,
            "payload": payload or {},
            "created_at": self._now_iso(),
        }
        with self._lock:
            self.tasks.append(task)
            self._write_state()
        return task

    def _handle_command(self, command: str) -> Dict[str, Any]:
        command_key = command.strip().lower()
        if command_key == "show status":
            return {
                "status": "ok",
                "queued_tasks": len(self.tasks),
                "processed_count": len(self.processed),
                "failed_count": len(self.failed),
                "results_count": len(self.results),
            }
        if command_key == "show heartbeat":
            return {"heartbeat": self.last_heartbeat}
        if command_key == "list memory":
            return {"memory": copy.deepcopy(self.memory)}
        if command_key == "list results":
            return {"results": copy.deepcopy(self.results)}
        raise ValueError(f"Unsupported command: {command}")

    def _process_generic_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        payload = task.get("payload", {})
        return {
            "task_id": task["id"],
            "kind": task["kind"],
            "echo": payload,
            "processed_at": self._now_iso(),
        }

    def _process_one(self) -> Optional[Dict[str, Any]]:
        with self._lock:
            if not self.tasks:
                return None
            task = self.tasks.popleft()

        try:
            if task["kind"] == "command":
                command = str(task.get("payload", {}).get("command", ""))
                result = {
                    "task_id": task["id"],
                    "kind": "command",
                    "command": command,
                    "output": self._handle_command(command),
                    "processed_at": self._now_iso(),
                }
            else:
                result = self._process_generic_task(task)

            with self._lock:
                self.processed.append(task)
                self.results.append(result)
                self._write_state()
            return result

        except Exception as exc:  # standard failure path for task processing
            failure = {
                "task": task,
                "error": str(exc),
                "failed_at": self._now_iso(),
            }
            with self._lock:
                self.failed.append(failure)
                self._write_state()
            return None

    def _heartbeat_loop(self) -> None:
        while not self._stop_event.is_set():
            with self._lock:
                self.last_heartbeat = self._now_iso()
                self._write_state()
            time.sleep(self.heartbeat_interval)

    def start(self) -> None:
        heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        heartbeat_thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        with self._lock:
            self._write_state()

    def run_forever(self, poll_interval: float = 0.5) -> None:
        self.start()
        try:
            while not self._stop_event.is_set():
                self._process_one()
                time.sleep(poll_interval)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()


def parse_payload(raw_payload: Optional[str]) -> Dict[str, Any]:
    if not raw_payload:
        return {}
    return json.loads(raw_payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ARKAI local command-aware agent.")
    parser.add_argument(
        "--heartbeat-interval",
        type=float,
        default=2.0,
        help="Heartbeat interval in seconds.",
    )
    parser.add_argument(
        "--add-task",
        action="append",
        metavar="KIND",
        help="Queue a task kind. Use with --payload for JSON payload.",
    )
    parser.add_argument(
        "--payload",
        action="append",
        metavar="JSON",
        help="JSON payload for --add-task (paired by position).",
    )
    parser.add_argument(
        "--run-seconds",
        type=float,
        default=None,
        help="Run for N seconds then exit. If omitted, run forever.",
    )
    args = parser.parse_args()

    agent = ArkaiAgent(heartbeat_interval=args.heartbeat_interval)

    task_kinds = args.add_task or []
    payloads = args.payload or []
    for idx, kind in enumerate(task_kinds):
        raw_payload = payloads[idx] if idx < len(payloads) else None
        agent.add_task(kind=kind, payload=parse_payload(raw_payload))

    if args.run_seconds is None:
        agent.run_forever()
        return

    agent.start()
    end_time = time.time() + args.run_seconds
    try:
        while time.time() < end_time:
            agent._process_one()
            time.sleep(0.25)
    finally:
        agent.stop()


if __name__ == "__main__":
    main()
