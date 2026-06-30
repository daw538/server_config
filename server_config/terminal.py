"""Terminal formatting and output utilities using Rich."""

import sys
from typing import Optional, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

# Create a global console instance
console = Console()


def print_header(text: str, title: Optional[str] = None) -> None:
    """Print a header with optional title."""
    if title:
        header = Text(f"{title}: {text}", style="bold cyan")
    else:
        header = Text(text, style="bold cyan")
    console.print(Panel(header, border_style="cyan"))


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]✗[/bold red] {message}")


def print_info(message: str) -> None:
    """Print an informational message."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_progress(message: str, done: bool = False) -> None:
    """Print a progress message."""
    if done:
        console.print(f"[bold green]✓[/bold green] {message}")
    else:
        console.print(f"[bold blue]→[/bold blue] {message}")


def print_section(title: str, content: str = "") -> None:
    """Print a section with a title and optional content."""
    console.print(f"\n[bold magenta]{title}[/bold magenta]")
    if content:
        console.print(content)


def format_path(path: str) -> str:
    """Format a file path for display."""
    return f"[dim]{path}[/dim]"


def format_command(cmd: str) -> str:
    """Format a command for display."""
    return f"[bold green]`{cmd}`[/bold green]"


def format_tool(name: str) -> str:
    """Format a tool name for display."""
    return f"[bold blue]{name}[/bold blue]"


def format_os(os_name: str) -> str:
    """Format an OS name for display."""
    colors = {
        "linux": "green",
        "macos": "cyan", 
        "windows": "blue"
    }
    color = colors.get(os_name.lower(), "white")
    return f"[bold {color}]{os_name}[/bold {color}]"


def format_rc_file(path: str) -> str:
    """Format a file path for display."""
    return f"[dim]{path}[/dim]"


class InstallationProgress:
    """Context manager for showing installation progress."""
    
    def __init__(self, description: str):
        self.description = description
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        )
    
    def __enter__(self):
        self.task = self.progress.add_task(self.description, total=None)
        self.progress.start()
        return self
    
    def update(self, message: str):
        self.progress.update(self.task, description=message)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress.stop()
