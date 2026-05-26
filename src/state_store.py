import csv
import sqlite3
from datetime import datetime
from pathlib import Path


class SQLiteStateStore:
    def __init__(self, database_path):
        self.database_path = Path(database_path)

    def initialize(self, schema_path="data/schema.sql"):
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        schema = Path(schema_path).read_text(encoding="utf-8")
        with sqlite3.connect(self.database_path) as connection:
            connection.executescript(schema)

    def seed_from_csv(self, adjacency_csv, connection_csv):
        with sqlite3.connect(self.database_path) as connection:
            self._seed_adjacencies(connection, adjacency_csv)
            self._seed_connections(connection, connection_csv)

    def get_entries(self, link_group):
        query = """
            SELECT node_name, node_neighbor, state, last_changed, link_group
            FROM isis_adjacencies
            WHERE link_group = ?
        """
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(query, (link_group,)).fetchall()
            return [dict(row) for row in rows]

    def update_adjacency_state(self, node_name, node_neighbor, state, event_epoch):
        last_changed = datetime.fromtimestamp(float(event_epoch)).strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(self.database_path) as connection:
            self._update_one_direction(connection, node_name.lower(), node_neighbor.lower(), state, last_changed)
            self._update_one_direction(connection, node_neighbor.lower(), node_name.lower(), state, last_changed)

    def get_connection(self, connection_name):
        query = """
            SELECT connection_name, product_uid, current_bandwidth_mbps
            FROM vxc_connections
            WHERE connection_name = ?
        """
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(query, (connection_name,)).fetchone()
            return dict(row) if row else None

    def record_bandwidth_change(self, connection_name, bandwidth_mbps, action, api_response):
        column_name = "upgrade_execution" if action == "upgrade" else "restore_execution"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = f"""
            UPDATE vxc_connections
            SET current_bandwidth_mbps = ?, {column_name} = ?, api_response = ?
            WHERE connection_name = ?
        """
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(query, (bandwidth_mbps, timestamp, api_response, connection_name))

    @staticmethod
    def _update_one_direction(connection, node_name, node_neighbor, state, last_changed):
        connection.execute(
            """
            UPDATE isis_adjacencies
            SET state = ?, last_changed = ?
            WHERE node_name = ? AND node_neighbor = ?
            """,
            (state, last_changed, node_name, node_neighbor),
        )

    @staticmethod
    def _seed_adjacencies(connection, csv_path):
        with Path(csv_path).open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            connection.executemany(
                """
                INSERT OR REPLACE INTO isis_adjacencies
                (node_name, node_neighbor, state, last_changed, link_group)
                VALUES (:node_name, :node_neighbor, :state, :last_changed, :link_group)
                """,
                reader,
            )

    @staticmethod
    def _seed_connections(connection, csv_path):
        with Path(csv_path).open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            connection.executemany(
                """
                INSERT OR REPLACE INTO vxc_connections
                (connection_name, product_uid, current_bandwidth_mbps)
                VALUES (:connection_name, :product_uid, :current_bandwidth_mbps)
                """,
                reader,
            )
