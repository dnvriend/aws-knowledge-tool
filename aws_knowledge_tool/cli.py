"""CLI entry point for aws-knowledge-tool.

Note: This code was generated with assistance from AI coding tools
and has been reviewed and tested by a human.
"""

import click

from aws_knowledge_tool.utils import get_greeting


@click.command()
@click.version_option(version="0.1.0")
def main() -> None:
    """A CLI that queries the AWS knowledge base"""
    click.echo(get_greeting())


if __name__ == "__main__":
    main()
