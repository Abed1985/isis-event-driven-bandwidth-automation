import argparse

from state_store import SQLiteStateStore


def parse_args():
    parser = argparse.ArgumentParser(description="Update an ISIS adjacency from an event payload.")
    parser.add_argument("node_name", help="Local node name from the event")
    parser.add_argument("node_neighbor", help="Neighbor node name from the event")
    parser.add_argument("state", choices=["up", "down"], help="New adjacency state")
    parser.add_argument("event_time", help="Event timestamp as epoch seconds")
    parser.add_argument("--database", default="data/demo_adjacency.db", help="SQLite database path")
    return parser.parse_args()


def main():
    args = parse_args()
    store = SQLiteStateStore(args.database)
    store.update_adjacency_state(args.node_name, args.node_neighbor, args.state, args.event_time)
    print(f"Updated {args.node_name}<->{args.node_neighbor} to {args.state}")


if __name__ == "__main__":
    main()
