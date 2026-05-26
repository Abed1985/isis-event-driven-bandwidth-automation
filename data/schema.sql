CREATE TABLE IF NOT EXISTS isis_adjacencies (
    node_name TEXT NOT NULL,
    node_neighbor TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('up', 'down')),
    last_changed TEXT NOT NULL,
    link_group TEXT NOT NULL,
    PRIMARY KEY (node_name, node_neighbor)
);

CREATE TABLE IF NOT EXISTS vxc_connections (
    connection_name TEXT PRIMARY KEY,
    product_uid TEXT NOT NULL,
    current_bandwidth_mbps INTEGER NOT NULL,
    upgrade_execution TEXT,
    restore_execution TEXT,
    api_response TEXT
);
