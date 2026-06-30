"""System information utilities for cross-platform support."""

import platform
import sys
import os
from typing import Tuple, Dict, Any
from dataclasses import dataclass
import socket
import psutil

from .terminal import console, print_info, format_os


@dataclass
class SystemInfo:
    """System information container."""
    os_name: str
    os_version: str
    architecture: str
    hostname: str
    python_version: str
    python_executable: str
    user: str
    cpu_cores: int
    total_memory_gb: float
    is_linux: bool
    is_macos: bool
    is_windows: bool


def get_system_info() -> SystemInfo:
    """Get comprehensive system information."""
    system = platform.system()
    os_name = system.lower()
    
    # Normalize OS names
    if os_name == "darwin":
        os_name = "macos"
    elif os_name == "windows":
        os_name = "windows"
    else:
        os_name = "linux"
    
    # Get memory info
    try:
        import psutil
        total_memory_gb = psutil.virtual_memory().total / (1024 ** 3)
        cpu_cores = psutil.cpu_count(logical=False) or 1
    except ImportError:
        # Fallback without psutil
        try:
            cpu_cores = os.cpu_count() or 1
        except (AttributeError, TypeError):
            cpu_cores = 1
        total_memory_gb = 0.0
    
    return SystemInfo(
        os_name=os_name,
        os_version=platform.release(),
        architecture=platform.machine(),
        hostname=socket.gethostname(),
        python_version=platform.python_version(),
        python_executable=sys.executable,
        user=os.getenv("USER", os.getenv("USERNAME", "unknown")),
        cpu_cores=cpu_cores,
        total_memory_gb=round(total_memory_gb, 2),
        is_linux=os_name == "linux",
        is_macos=os_name == "macos",
        is_windows=os_name == "windows"
    )


def get_os_type() -> str:
    """Get the current operating system type."""
    system_info = get_system_info()
    if system_info.is_linux:
        return "linux"
    elif system_info.is_macos:
        return "macos"
    elif system_info.is_windows:
        return "windows"
    else:
        return "unknown"


def get_platform_info() -> Dict[str, Any]:
    """Get platform-specific information as a dictionary."""
    info = get_system_info()
    return {
        "os": info.os_name,
        "version": info.os_version,
        "arch": info.architecture,
        "hostname": info.hostname,
        "python": info.python_version,
        "user": info.user,
        "cores": info.cpu_cores,
        "memory_gb": info.total_memory_gb,
    }


def print_system_info() -> None:
    """Print formatted system information."""
    info = get_system_info()
    
    console.print()
    console.rule("[bold cyan]System Information[/bold cyan]")
    
    # OS Info
    os_label = format_os(info.os_name)
    console.print(f"  Operating System: {os_label} {info.os_version}")
    console.print(f"  Architecture:     {info.architecture}")
    
    # Python Info
    console.print(f"  Python:           {info.python_version} ({info.python_executable})")
    
    # Hardware Info
    console.print(f"  CPU Cores:        {info.cpu_cores}")
    console.print(f"  Total Memory:    {info.total_memory_gb} GB")
    
    # Network Info
    console.print(f"  Hostname:         {info.hostname}")
    console.print(f"  User:            {info.user}")
    
    console.rule()


def check_required_dependencies() -> Tuple[bool, list]:
    """Check for required system dependencies."""
    missing = []
    
    # Check for git
    try:
        import subprocess
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            missing.append("git")
    except FileNotFoundError:
        missing.append("git")
    
    # Check for curl (common dependency for installing tools)
    try:
        import subprocess
        result = subprocess.run(["curl", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            missing.append("curl")
    except FileNotFoundError:
        missing.append("curl")
    
    return len(missing) == 0, missing


# CLI entry point
import click


@click.command()
@click.option("--json", "-j", is_flag=True, help="Output in JSON format")
def main(json: bool):
    """Display system information."""
    if json:
        import json as json_module
        info = get_system_info()
        output = {
            "os": info.os_name,
            "version": info.os_version,
            "architecture": info.architecture,
            "hostname": info.hostname,
            "python_version": info.python_version,
            "python_executable": info.python_executable,
            "user": info.user,
            "cpu_cores": info.cpu_cores,
            "total_memory_gb": info.total_memory_gb,
        }
        click.echo(json_module.dumps(output, indent=2))
    else:
        print_system_info()


if __name__ == "__main__":
    main()
