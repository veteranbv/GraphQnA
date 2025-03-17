"""Command modules for the CLI."""

from graphqna.cli.commands.db import configure_parser, execute
from graphqna.cli.commands.ingest import configure_parser, execute
from graphqna.cli.commands.query import configure_parser, execute
from graphqna.cli.commands.test import configure_parser, execute