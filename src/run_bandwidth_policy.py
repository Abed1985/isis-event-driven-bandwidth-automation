import argparse
from pathlib import Path

import yaml

from megaport_api import MegaportClient
from opevents import OpeventsClient
from policy import PolicyTiming, decide_bandwidth_action
from state_store import SQLiteStateStore


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate ISIS link state and adjust Megaport VXC bandwidth.")
    parser.add_argument("--config", default="config.example.yaml", help="YAML config path")
    return parser.parse_args()


def load_config(config_path):
    return yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))


def main():
    args = parse_args()
    config = load_config(args.config)
    dry_run = bool(config.get("dry_run", True))
    store = SQLiteStateStore(config["database_path"])
    megaport = MegaportClient(dry_run=dry_run)
    opevents = OpeventsClient(dry_run=dry_run)
    timing = PolicyTiming(**config.get("policy", {}))
    access_token = megaport.get_access_token()

    for link in config["links"]:
        connection = store.get_connection(link["name"])
        if not connection:
            print(f"Skipping {link['name']}: connection not found in database")
            continue

        entries = store.get_entries(link["link_group"])
        current_bandwidth = megaport.get_product_bandwidth(access_token, connection["product_uid"])
        current_bandwidth = current_bandwidth or int(connection["current_bandwidth_mbps"])
        action, target_bandwidth = decide_bandwidth_action(
            entries,
            current_bandwidth,
            int(link["upgrade_bandwidth_mbps"]),
            timing,
        )
        if action == "none":
            print(f"{link['name']}: no bandwidth change required")
            continue

        api_response = megaport.update_product_bandwidth(access_token, connection["product_uid"], target_bandwidth)
        store.record_bandwidth_change(link["name"], target_bandwidth, action, api_response)
        priority_key = "event_priority_upgrade" if action == "upgrade" else "event_priority_restore"
        event = f"{config['opevents']['event_prefix']} - {link['name']}"
        event_response = opevents.create_event(
            config["opevents"]["node"],
            event,
            api_response,
            target_bandwidth,
            link[priority_key],
        )
        print(api_response)
        print(event_response)


if __name__ == "__main__":
    main()
