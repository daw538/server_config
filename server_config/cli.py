#!/usr/bin/env python3
"""Main CLI entry point for server_config."""

import click

from .terminal import print_header, print_info
from .system_info import print_system_info
from .install import cli_install as install_cli


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def main(verbose: bool):
    """Server configuration tools for research environments.
    
    This tool helps configure a standard set of utilities across different
    research computers (Linux, MacOS, Windows) using pixi package management.
    """
    if verbose:
        print_header("Server Configuration CLI")
        print_system_info()


@main.command()
@click.option("--json", "-j", is_flag=True, help="Output in JSON format")
def info(json: bool):
    """Display system information."""
    from .system_info import main as system_info_main
    print_header("System Information")
    system_info_main(json)


@main.command()
def check():
    """Check which tools are already installed."""
    from .install import TOOLS_CONFIG, is_tool_installed, format_tool
    from .terminal import print_success, print_error, format_tool
    
    print_header("Tool Status Check")
    
    for tool_name, config in TOOLS_CONFIG.items():
        if is_tool_installed(tool_name):
            print_success(f"{format_tool(tool_name)}: installed")
        else:
            print_error(f"{format_tool(tool_name)}: not installed")


# Add the install subcommand
def add_install_commands():
    """Add install commands to the main CLI."""
    main.add_command(install_cli, "install")


# Initialize the CLI
add_install_commands()


if __name__ == "__main__":
    main()
