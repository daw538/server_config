"""Installation module for configuring tools across platforms."""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime
import enum

import click

from .terminal import (
    console, print_header, print_success, print_error, print_info, 
    print_warning, print_section, format_tool, format_os, format_command, format_rc_file
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


# Tool configuration with platform constraints
TOOLS_CONFIG = {
    "pixi": {
        "description": "Cross-platform package manager",
        "priority": 10,  # Should be installed first
        "platforms": ["linux", "macos"],  # Pixi supports these platforms
        "install": {
            "linux": "curl -fsSL https://pixi.sh/install.sh | sh",
            "macos": "curl -fsSL https://pixi.sh/install.sh | sh",
        },
        "check": "pixi --version",
        "env_var": "PIXI_HOME",
        "shell_config": {
            "path": 'export PATH="$HOME/.pixi/bin:$PATH"',
            "description": "Add pixi to PATH"
        }
    },
    "dust": {
        "description": "A more powerful du alternative",
        "priority": 1,
        "platforms": ["linux", "macos", "windows"],
        "install": {
            "pixi": "pixi global install dust",
            "brew": "brew install dust",
            "apt": "sudo apt install dust",
            "yum": "sudo yum install dust",
            "choco": "choco install dust",
        },
        "check": "dust --version",
        "env_var": None,
    },
    "duf": {
        "description": "Disk usage analyzer",
        "priority": 1,
        "platforms": ["linux", "macos", "windows"],
        "install": {
            "pixi": "pixi global install duf",
            "brew": "brew install duf",
            "apt": "sudo apt install duf",
            "yum": "sudo yum install duf",
            "choco": "choco install duf",
        },
        "check": "duf --version",
        "env_var": None,
    },
    "bat": {
        "description": "A cat(1) clone with syntax highlighting",
        "priority": 1,
        "platforms": ["linux", "macos", "windows"],
        "install": {
            "pixi": "pixi global install bat",
            "brew": "brew install bat",
            "apt": "sudo apt install bat",
            "yum": "sudo yum install bat",
            "choco": "choco install bat",
        },
        "check": "bat --version",
        "env_var": None,
    },
    "htop": {
        "description": "Interactive process viewer",
        "priority": 1,
        "platforms": ["linux", "macos"],  # Not available on Windows natively
        "install": {
            "pixi": "pixi global install htop",
            "brew": "brew install htop",
            "apt": "sudo apt install htop",
            "yum": "sudo yum install htop",
        },
        "check": "htop --version",
        "env_var": None,
        "windows_note": "htop is not available for native Windows. Consider using Windows Terminal or WSL.",
    },
    "starship": {
        "description": "Minimal, lightning-fast shell prompt",
        "priority": 1,
        "platforms": ["linux", "macos", "windows"],
        "install": {
            "pixi": "pixi global install starship",
            "brew": "brew install starship",
            "curl_script": "curl -sS https://starship.rs/install.sh | sh -s -- -y",
        },
        "check": "starship --version",
        "env_var": None,
        "config_file": "config/starship.toml",
        "shell_config": {
            "zsh": 'eval "$(starship init zsh)"',
            "bash": 'eval "$(starship init bash)"',
            "fish": "starship init fish | source",
            "description": "Initialize starship prompt"
        }
    },
    "vibe": {
        "description": "Vibe CLI - AI coding assistant",
        "priority": 1,
        "platforms": ["linux", "macos", "windows"],
        "install": {
            "pixi": "pixi global install mistral-vibe",
            "curl_script": "curl -sSL https://vibe.dev/install.sh | sh",
        },
        "check": "vibe --version",
        "env_var": None,
        "config_file": "config/vibe.toml",
        "shell_config": None,
    },
}


def get_tool_config(tool_name: str) -> Optional[Dict]:
    """Get configuration for a specific tool."""
    return TOOLS_CONFIG.get(tool_name.lower())


def is_platform_supported(tool_name: str, os_type: str) -> bool:
    """Check if a tool supports the current platform."""
    config = get_tool_config(tool_name)
    if not config:
        return False
    
    # If no platform constraints, assume all platforms supported
    if "platforms" not in config:
        return True
    
    return os_type in config["platforms"]


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
    if "pixi" in install_options and is_tool_installed("pixi"):
        return install_options["pixi"]
    
    # Try OS-specific install command
    if os_type in install_options:
        return install_options[os_type]
    
    # Try curl_script as fallback for some tools
    if "curl_script" in install_options:
        return install_options["curl_script"]
    
    return None


def install_tool(tool_name: str, force: bool = False) -> Tuple[bool, Optional[str]]:
    """Install a single tool. Returns (success, message)."""
    os_type = get_os_type()
    config = get_tool_config(tool_name)
    
    if not config:
        return False, f"Unknown tool: {tool_name}"
    
    # Check platform support
    if not is_platform_supported(tool_name, os_type):
        windows_note = config.get("windows_note", "")
        return False, f"{tool_name} is not available on {os_type}. {windows_note}"
    
    tool_label = format_tool(tool_name)
    os_label = format_os(os_type)
    
    # Check if already installed
    if not force and is_tool_installed(tool_name):
        return True, f"{tool_name} is already installed"
    
    # Get install command
    install_cmd = get_install_command(tool_name, os_type)
    if not install_cmd:
        return False, f"No installation method available for {tool_name} on {os_type}"
    
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
            return True, f"Successfully installed {tool_name}"
        else:
            return False, f"Failed to install {tool_name}: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, f"Installation of {tool_name} timed out"
    except Exception as e:
        return False, f"Error installing {tool_name}: {str(e)}"


def install_multiple_tools(tools: List[str], force: bool = False) -> Dict[str, Tuple[bool, Optional[str]]]:
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
        success, message = install_tool(tool, force)
        results[tool] = (success, message)
    
    return results


# Shell configuration functions

def detect_shell() -> Optional[str]:
    """Detect the current shell."""
    # Check SHELL environment variable
    shell = os.getenv("SHELL", "")
    
    if shell:
        shell = shell.split("/")[-1]  # Get basename
        if shell in ["bash", "zsh", "fish", "csh", "tcsh", "sh", "dash"]:
            return shell
    
    # Check common shells by trying to read their rc files
    home = str(Path.home())
    possible_shells = [
        ("zsh", f"{home}/.zshrc"),
        ("bash", f"{home}/.bashrc"),
        ("fish", f"{home}/.config/fish/config.fish"),
    ]
    
    for shell_name, rc_file in possible_shells:
        if Path(rc_file).exists():
            return shell_name
    
    # Default to bash
    return "bash"


def find_rc_file(shell: str) -> Optional[str]:
    """Find the appropriate rc file for the given shell."""
    home = str(Path.home())
    
    rc_files = {
        "zsh": f"{home}/.zshrc",
        "bash": f"{home}/.bashrc",
        "fish": f"{home}/.config/fish/config.fish",
        "csh": f"{home}/.cshrc",
        "tcsh": f"{home}/.tcshrc",
        "sh": f"{home}/.profile",
        "dash": f"{home}/.profile",
    }
    
    return rc_files.get(shell)


def create_backup(rc_file: str) -> Optional[str]:
    """Create a backup of the rc file. Returns backup path or None."""
    rc_path = Path(rc_file)
    if not rc_path.exists():
        return None
    
    # Create backup with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path.home() / ".server_config_backups"
    backup_dir.mkdir(exist_ok=True)
    
    backup_filename = f"{rc_path.name}.{timestamp}.bak"
    backup_path = backup_dir / backup_filename
    
    try:
        shutil.copy2(rc_file, str(backup_path))
        return str(backup_path)
    except Exception as e:
        print_error(f"Failed to create backup: {str(e)}")
        return None


def get_shell_init_commands(shell: str) -> List[Dict[str, str]]:
    """Get the shell initialization commands for tools that need them."""
    commands = []
    
    # Pixi PATH addition
    pixi_config = get_tool_config("pixi")
    if pixi_config and "shell_config" in pixi_config:
        commands.append({
            "tool": "pixi",
            "command": pixi_config["shell_config"]["path"],
            "description": pixi_config["shell_config"]["description"],
            "required": True
        })
    
    # Starship initialization
    starship_config = get_tool_config("starship")
    if starship_config and "shell_config" in starship_config:
        if shell in starship_config["shell_config"]:
            commands.append({
                "tool": "starship",
                "command": starship_config["shell_config"][shell],
                "description": starship_config["shell_config"]["description"],
                "required": True  # Prompt with default yes for starship
            })
    
    return commands


def copy_config_file(tool_name: str) -> bool:
    """Copy configuration file for a tool to user's config directory."""
    config = get_tool_config(tool_name)
    if not config or "config_file" not in config:
        print_warning(f"No configuration file defined for {tool_name}")
        return False
    
    config_filename = config["config_file"]
    config_path = Path(__file__).parent.parent / config_filename
    
    if not config_path.exists():
        print_warning(f"Configuration file {config_filename} not found in repository")
        return False
    
    # Determine target path based on tool
    if tool_name == "starship":
        target_dir = Path.home() / ".config"
        target_filename = config_path.name
    elif tool_name == "vibe":
        target_dir = Path.home() / ".vibe"
        target_filename = config_path.name
    else:
        print_warning(f"Unknown target directory for {tool_name} configuration")
        return False
    
    target_path = target_dir / target_filename
    
    try:
        target_dir.mkdir(exist_ok=True)
        
        # Create backup if file exists
        if target_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = target_dir / f"{target_filename}.{timestamp}.bak"
            shutil.copy2(target_path, backup_path)
            print_info(f"Backed up existing {target_filename} to {backup_path}")
        
        shutil.copy2(config_path, target_path)
        print_success(f"Copied {tool_name} configuration to {target_path}")
        return True
        
    except Exception as e:
        print_error(f"Failed to copy {tool_name} configuration: {str(e)}")
        return False


def copy_starship_config() -> bool:
    """Copy starship configuration to ~/.config/starship.toml"""
    return copy_config_file("starship")


def copy_vibe_config() -> bool:
    """Copy vibe configuration to ~/.vibe/vibe.toml"""
    return copy_config_file("vibe")


def prompt_for_shell_config(shell: str, rc_file: str) -> bool:
    """Handle shell configuration with user prompts."""
    os_type = get_os_type()
    
    # Skip shell configuration on Windows for now
    if os_type == "windows":
        print_info("Shell configuration is not automatically supported on Windows.")
        print_info("Please manually configure your terminal profile.")
        print_info("You may need to add:")
        print_info("  - Pixi to PATH: export PATH=\"$HOME/.pixi/bin:$PATH\"")
        if "starship" in [tool.lower() for tool in TOOLS_CONFIG.keys()]:
            print_info("  - Starship initialization: eval \"$(starship init <your_shell>)\"")
        return False
    
    # Get shell initialization commands
    shell_commands = get_shell_init_commands(shell)
    
    if not shell_commands:
        print_info("No shell configuration needed for installed tools.")
        return False
    
    print_section("Shell Configuration")
    print_info(f"Detected shell: {format_tool(shell)}")
    print_info(f"RC file: {format_rc_file(rc_file)}")
    
    modified = False
    
    for cmd_info in shell_commands:
        command = cmd_info["command"]
        description = cmd_info["description"]
        required = cmd_info.get("required", False)
        tool_name = cmd_info["tool"]
        
        print_section(f"{description} ({tool_name})")
        
        # Check if already in rc file
        rc_path = Path(rc_file)
        if rc_path.exists():
            content = rc_path.read_text()
            if command.strip() in content:
                print_success(f"'{command}' already present in {rc_file}")
                continue
        
        print_info(f"This will add the following to {rc_file}:")
        console.print(f"  [bold green]{command}[/bold green]")
        
        if required:
            print_info("(This is required for tool functionality)")
        else:
            print_info("(This is optional but recommended)")
        
        # Ask for confirmation
        if required:
            response = input(f"Add {description} to {rc_file}? [Y/n]: ").strip().lower()
        else:
            response = input(f"Add {description} to {rc_file}? [y/N]: ").strip().lower()
        
        if response == "" and required:
            response = "y"  # Default to yes for required items
        elif response == "" and not required:
            response = "n"  # Default to no for optional items
        
        if response.startswith("y"):
            # Create backup if it doesn't exist
            backup_path = create_backup(rc_file)
            if backup_path:
                print_success(f"Created backup: {backup_path}")
            
            # Add the command to the rc file
            try:
                with open(rc_file, "a") as f:
                    f.write(f"\n# Added by server_config ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")
                    f.write(f"{command}\n")
                
                print_success(f"Added {description} to {rc_file}")
                modified = True
                
            except Exception as e:
                print_error(f"Failed to modify {rc_file}: {str(e)}")
        else:
            print_info(f"Skipped {description}")
    
    if modified:
        print_success("Shell configuration updated!")
        print_info("Changes will take effect in new shell sessions.")
        print_info("To apply changes now, run: exec <shell> (e.g., 'exec bash' or 'exec zsh')")
    
    return modified


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
    success, message = install_tool("pixi")
    if not success:
        print_error(message)
        return False
    
    print_success(message)
    
    # Initialize pixi in current directory if pixi.toml exists
    script_dir = Path(__file__).parent.parent
    if (script_dir / "pixi.toml").exists():
        try:
            result = subprocess.run(
                ["pixi", "sync"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(script_dir)
            )
            if result.returncode == 0:
                print_success("Pixi project synchronized")
            else:
                print_warning("Pixi project sync failed, but pixi might still work")
        except Exception:
            print_warning("Cannot sync pixi project")
    
    return check_pixi_environment()


# Terminal formatting helper



@click.group(name="install")
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def cli_install(verbose: bool):
    """Install configuration tools on this system."""
    if verbose:
        from .system_info import print_system_info
        print_system_info()
    
    # Check required dependencies
    has_deps, missing = check_required_dependencies()
    if not has_deps:
        print_warning(f"Missing required system dependencies: {', '.join(missing)}")
        print_info("Installing may not work without these dependencies")


@cli_install.command()
@click.option("--force", "-f", is_flag=True, help="Force reinstall even if already installed")
@click.option("--tool", "-t", multiple=True, help="Specific tool to install")
@click.option("--skip-shell", is_flag=True, help="Skip shell configuration prompts")
def all_ls(force: bool, tool: List[str], skip_shell: bool):
    """Install all configured tools."""
    print_header("Server Configuration - Install Tools")
    
    # Filter tools by platform
    os_type = get_os_type()
    available_tools = []
    skipped_tools = []
    
    if tool:
        # Install specific tools
        tools_to_install = tool
    else:
        # Install all known tools
        tools_to_install = list(TOOLS_CONFIG.keys())
    
    for t in tools_to_install:
        if is_platform_supported(t, os_type):
            available_tools.append(t)
        else:
            skipped_tools.append(t)
    
    if skipped_tools:
        print_info(f"Skipping tools not available on {os_type}: {', '.join(skipped_tools)}")
    
    print_info(f"Installing tools: {', '.join(available_tools)}")
    
    results = install_multiple_tools(available_tools, force)
    
    print_section("Installation Summary")
    success_count = sum(1 for success, _ in results.values() if success)
    total_count = len(results)
    
    for tool_name, (success, message) in results.items():
        if success:
            print_success(f"{tool_name}: {message}")
        else:
            print_error(f"{tool_name}: {message}")
    
    console.print(f"\n[bold]Summary:[/bold] {success_count}/{total_count} tools installed successfully")
    
    # Handle configuration file deployment
    config_tools = ["starship", "vibe"]
    for tool_name in config_tools:
        if tool_name in results and results[tool_name][0]:
            print_info(f"{tool_name.capitalize()} installed successfully!")
            response = input(f"Would you like to install the {tool_name} configuration file? [Y/n]: ").strip().lower()
            if response == "" or response.startswith("y"):
                if tool_name == "starship":
                    copy_starship_config()
                elif tool_name == "vibe":
                    copy_vibe_config()
    
    # Handle shell configuration
    if not skip_shell:
        shell = detect_shell()
        if shell:
            rc_file = find_rc_file(shell)
            if rc_file:
                prompt_for_shell_config(shell, rc_file)
            else:
                print_warning(f"Cannot find RC file for detected shell: {shell}")
        else:
            print_warning("Could not detect your shell")


@cli_install.command()
@click.argument("tool_name")
@click.option("--force", "-f", is_flag=True, help="Force reinstall even if already installed")
def tool(force: bool, tool_name: str):
    """Install a specific tool."""
    print_header(f"Install {tool_name}")
    
    success, message = install_tool(tool_name, force)
    if success:
        print_success(f"{tool_name} installed successfully: {message}")
    else:
        print_error(f"Failed to install {tool_name}: {message}")
    
    # Handle configuration file deployment for tools with configs
    if tool_name.lower() in ["starship", "vibe"] and success:
        response = input(f"Would you like to install the {tool_name} configuration file? [Y/n]: ").strip().lower()
        if response == "" or response.startswith("y"):
            if tool_name == "starship":
                copy_starship_config()
            elif tool_name == "vibe":
                copy_vibe_config()


@cli_install.command()
def configure_shell():
    """Configure shell rc files for installed tools."""
    print_header("Configure Shell")
    
    shell = detect_shell()
    if not shell:
        print_error("Could not detect your shell")
        return
    
    rc_file = find_rc_file(shell)
    if not rc_file:
        print_error(f"Cannot find RC file for shell: {shell}")
        return
    
    print_info(f"Detected shell: {shell}")
    print_info(f"RC file: {format_rc_file(rc_file)}")
    
    prompt_for_shell_config(shell, rc_file)


@cli_install.command()
def copy_starship_config_cmd():
    """Copy starship configuration file to user's config directory."""
    print_header("Install Starship Configuration")
    copy_starship_config()


@cli_install.command()
def copy_vibe_config_cmd():
    """Copy vibe configuration file to user's config directory."""
    print_header("Install Vibe Configuration")
    copy_vibe_config()


@cli_install.command()
def copy_all_configs_cmd():
    """Copy all configuration files to user's config directories."""
    print_header("Install All Configurations")
    copy_starship_config()
    copy_vibe_config()


def main():
    """Main entry point for installation."""
    from .system_info import print_system_info
    print_system_info()
    cli_install()


if __name__ == "__main__":
    main()
