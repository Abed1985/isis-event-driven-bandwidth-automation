import argparse

from state_store import SQLiteStateStore


def parse_args():
    parser = argparse.ArgumentParser(description="Create and seed the demo SQLite database.")
    parser.add_argument("--database", default="data/demo_adjacency.db", help="SQLite database path")
    parser.add_argument("--schema", default="data/schema.sql", help="SQL schema path")
    parser.add_argument("--adjacencies", default="data/sample_adjacencies.csv", help="Sample ISIS adjacency CSV")
    parser.add_argument("--connections", default="data/sample_connections.csv", help="Sample VXC connection CSV")
    return parser.parse_args()


def main():
    args = parse_args()
    store = SQLiteStateStore(args.database)
    store.initialize(args.schema)
    store.seed_from_csv(args.adjacencies, args.connections)
    print(f"Initialized {args.database}")


if __name__ == "__main__":
    main()
