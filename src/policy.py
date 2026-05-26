from dataclasses import dataclass
from datetime import datetime


TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


@dataclass(frozen=True)
class PolicyTiming:
    down_after_seconds: int = 300
    stable_after_seconds: int = 900
    baseline_bandwidth_mbps: int = 10


def any_link_down(entries, now=None, down_after_seconds=300):
    now = now or datetime.now()
    for entry in entries:
        last_changed = datetime.strptime(entry["last_changed"], TIME_FORMAT)
        age_seconds = (now - last_changed).total_seconds()
        if entry["state"] == "down" and age_seconds >= down_after_seconds:
            return True
    return False


def all_links_up_stable(entries, now=None, stable_after_seconds=900):
    now = now or datetime.now()
    if not entries:
        return False

    for entry in entries:
        last_changed = datetime.strptime(entry["last_changed"], TIME_FORMAT)
        age_seconds = (now - last_changed).total_seconds()
        if entry["state"] != "up" or age_seconds < stable_after_seconds:
            return False
    return True


def decide_bandwidth_action(entries, current_bandwidth_mbps, target_bandwidth_mbps, timing, now=None):
    if any_link_down(entries, now=now, down_after_seconds=timing.down_after_seconds):
        if current_bandwidth_mbps == timing.baseline_bandwidth_mbps:
            return "upgrade", target_bandwidth_mbps
        return "none", current_bandwidth_mbps

    if all_links_up_stable(entries, now=now, stable_after_seconds=timing.stable_after_seconds):
        if current_bandwidth_mbps != timing.baseline_bandwidth_mbps:
            return "restore", timing.baseline_bandwidth_mbps

    return "none", current_bandwidth_mbps
