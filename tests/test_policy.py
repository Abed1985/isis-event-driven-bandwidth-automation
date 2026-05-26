from datetime import datetime

from src.policy import PolicyTiming, all_links_up_stable, any_link_down, decide_bandwidth_action


NOW = datetime(2026, 5, 26, 10, 0, 0)


def test_any_link_down_after_threshold():
    entries = [
        {"state": "down", "last_changed": "2026-05-26 09:54:00"},
        {"state": "up", "last_changed": "2026-05-26 09:00:00"},
    ]
    assert any_link_down(entries, now=NOW, down_after_seconds=300) is True


def test_all_links_up_stable_requires_every_link():
    entries = [
        {"state": "up", "last_changed": "2026-05-26 09:40:00"},
        {"state": "down", "last_changed": "2026-05-26 09:40:00"},
    ]
    assert all_links_up_stable(entries, now=NOW, stable_after_seconds=900) is False


def test_decide_upgrade_from_baseline_when_link_down():
    entries = [{"state": "down", "last_changed": "2026-05-26 09:50:00"}]
    action, bandwidth = decide_bandwidth_action(entries, 10, 1000, PolicyTiming(), now=NOW)
    assert action == "upgrade"
    assert bandwidth == 1000


def test_decide_restore_when_all_links_stable():
    entries = [
        {"state": "up", "last_changed": "2026-05-26 09:30:00"},
        {"state": "up", "last_changed": "2026-05-26 09:30:00"},
    ]
    action, bandwidth = decide_bandwidth_action(entries, 1000, 1000, PolicyTiming(), now=NOW)
    assert action == "restore"
    assert bandwidth == 10
