import os
import shlex
import subprocess


class OpeventsClient:
    def __init__(self, cli_path=None, dry_run=True):
        self.cli_path = cli_path or os.getenv("OPEVENTS_CLI_PATH", "/usr/local/omk/bin/opevents-cli.pl")
        self.dry_run = dry_run

    def create_event(self, node, event, details, element, priority):
        command = [
            "sudo",
            self.cli_path,
            "act=create-event",
            f"node={node}",
            f"event={event}",
            f"details={details}",
            f"element={element}Mbps",
            "action_required=1",
            "action_checked=0",
            f"priority={priority}",
        ]
        if self.dry_run:
            return "DRY RUN: would run " + " ".join(shlex.quote(part) for part in command)

        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout.strip()
