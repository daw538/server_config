"""Installation module for configuring tools across platforms."""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import enum

import click

from .terminal import (
    console, print_header, print_success, print_error, print_info, 
    print_warning, print_section, format_tool, format_os, format_command
)
from .system_info import get_system_info, get_os_type, check_required_dependencies


class InstallMethod(enum.Enum):
    """Installation methods for tools."""
    PIXI = "pixi"
    BREW = "brew"
    APT = "apt"
    YUM = "yum"
    CHOCO = "choco"
    WINGET = "winget"
    CURL_SCRIPT = "curl_script"
    BINARY = "binary"


# Tool configuration
TOOLS_CONFIG = {
    "pixi": {
        "description": "Package manager",
        "priority": 10,  # Should be installed first
        "install": {
            " linux": "curl -fsSL https://pixi.sh/install.sh | sh",
            "macos": "curl -fsSL https://pixi.sh/install.sh | sh",
            "windows": "powershell -c \"iwr -useb https://pixi.sh/install.ps1 | iex\""
        },
        "check": "pixi --version",
        "env_var": "PIXI_HOME",
    },
    "dust": {
        "description": "A more powerful du alternative",
        "priority": 1,
        "install": {
            "pixi": "pixi global install dust",
            "brew": "brew install dust",
            "apt": "sudo apt install dust",
            "yum": "sudo yum install dust",
        },
        "check": "dust --version",
        "env_var": None,
    },
    "duf": {
        "description": "Disk usage analyzer",
        "priority": 1,
        "install": {
            "pixi": "pixi global install duf",
            "brew": "brew install duf",
            "apt": "sudo apt install duf",
            "yum": "sudo yum install duf",
        },
        "check": "duf --version",
        "env_var": None,
    },
    "bat": {
        "description": "A cat(1) clone with syntax highlighting",
        "priority": 1,
        "install": {
            "pixi": "pixi global install bat",
            "brew": "brew install bat",
            "apt": "sudo apt install bat",
            "yum": "sudo yum install bat",
        },
        "check": "bat --version",
        "env_var": None,
    },
}


def get_tool_config(tool_name: str) -> Optional[Dict]:
    """Get configuration for a specific tool."""
    return TOOLS_CONFIG.get(tool_name.lower())


def is_tool_installed(tool_name: str) -> bool:
    """Check if a tool is already installed."""
    config = get_tool_config(tool_name)
    if not config or "check" not in config:
        return False
    
    check_cmd = config["check"]
    try:
        result = subprocess.run(
            check_cmd.split(), 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False


def get_install_command(tool_name: str, os_type: str) -> Optional[str]:
    """Get the appropriate install command for a tool on the specified OS."""
    config = get_tool_config(tool_name)
    if not config or "install" not in config:
        return None
    
    install_options = config["install"]
    
    # Try pixi first if pixi is available
    if "pixi" in install_options:
        pixi_cmd = install_options["pixi"]
        if is_tool_installed("pixi"):
            return pixi_cmd
    
    # Try OS-specific install command
    os_key = os_type
    if os_key in install_options:
        return install_options[os_key]
    
    return None


def install_tool(tool_name: str, force: bool = False) -> bool:
    """Install a single tool."""
    os_type = get_os_type()
    config = get_tool_config(tool_name)
    
    if not config:
        print_error(f"Unknown tool: {tool_name}")
        return False
    
    tool_label = format_tool(tool_name)
    os_label = format_os(os_type)
    
    # Check if already installed
    if not force and is_tool_installed(tool_name):
        print_success(f"{tool_label} is already installed")
        return True
    
    # Get install command
    install_cmd = get_install_command(tool_name, os_type)
    if not install_cmd:
        print_error(f"No installation method available for {tool_label} on {os_label}")
        return False
    
    print_info(f"Installing {tool_label} on {os_label}...")
    print_info(f"Running: {format_command(install_cmd)}")
    
    try:
        result = subprocess.run(
            install_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print_success(f"Successfully installed {tool_label}")
            return True
        else:
            print_error(f"Failed to install {tool_label}")
            if result.stderr:
                console.print(f"[dim]Error output:[/dim]\n{result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print_error(f"Installation of {tool_label} timed out")
        return False
    except Exception as e:
        print_error(f"Error installing {tool_label}: {str(e)}")
        return False


def install_multiple_tools(tools: List[str], force: bool = False) -> Dict[str, bool]:
    """Install multiple tools and return results."""
    results = {}
    
    # Sort tools by priority (ensure pixi is installed first)
    tool_priorities = []
    for tool in tools:
        config = get_tool_config(tool)
        priority = config.get("priority", 1) if config else 1
        tool_priorities.append((priority, tool))
    
    # Sort by priority (lower number = higher priority)
    tool_priorities.sort(key=lambda x: x[0])
    sorted_tools = [tool for _, tool in tool_priorities]
    
    for tool in sorted_tools:
        results[tool] = install_tool(tool, force)
    
    return results


def check_pixi_environment() -> bool:
    """Check if pixi environment is properly set up."""
    try:
        result = subprocess.run(
            ["pixi", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def setup_pixi_project() -> bool:
    """Set up the pixi project environment."""
    if check_pixi_environment():
        print_success("Pixi is already installed")
        return True
    
    print_info("Setting up Pixi environment...")
    
    # Try to install pixi
    os_type = get_os_type()
    if not install_tool("pixi"):
        return False
    
    # Initialize pixi in current directory if pixi.toml exists
    if Path("pixi.toml").exists():
        try:
            result = subprocess.run(
                ["pixi", "sync"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=Path.cwd()
            )
            if result.returncode == 0:
                print_success("Pixi project synchronized")
            else:
                print_warning("Pixi project sync failed, but pixi might still work")
        except Exception:
            print_warning("Cannot sync pixi project")
    
    return check_pixi_environment()


@click.group(name="install")
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def cli_install(verbose: bool):
    """Install configuration tools on this system."""
    if verbose:
        print_system_info()
    
    # Check required dependencies
    has_deps, missing = check_required_dependencies()
    if not has_deps:
        print_warning(f"Missing required system dependencies: {', '.join(missing)}")
        print_info("Installing may not work without these dependencies")


@cli_install.command()
@click.option("--force", "-f", is_flag=True, help="Force reinstall even if already installed")
@click.option("--tool", "-t", multiple=True, help="Specific tool to install")
def all_ls(force: bool, tool: List[str]):
    """Install all configured tools."""
    print_header("Server Configuration - Install Tools")
    
    if tool:
        # Install specific tools
        tools_to_install = tool
    else:
        # Install all known tools
        tools_to_install = list(TOOLS_CONFIG.keys())
    
    print_info(f"Installing tools: {', '.join(tools_to_install)}")
    
    results = install_multiple_tools(tools_to_install, force)
    
    print_section("Installation Summary")
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    for tool_name, success in results.items():
        if success:
            print_success(f"{tool_name}: installed")
        else:
            print_error(f"{tool_name}: failed")
    
    console.print(f"\n[bold]Summary:[/bold] {success_count}/{total_count} tools installed successfully")


@cli_install.command()
@click.argument("tool_name")
@click.option("--force", "-f", is_flag=True, help="Force reinstall even if already installed")
def tool(force: bool, tool_name: str):
    """Install a specific tool."""
    print_header(f"Install {tool_name}")
    
    if install_tool(tool_name, force):
        print_success(f"{tool_name} installed successfully")
        sys.exit(0)
    else:
        print_error(f"Failed to install {tool_name}")
        sys.exit(1)


def main():
    """Main entry point for installation."""
    print_system_info()
    cli_install()


if __name__ == "__main__":
    main()
