"""Server configuration tools for cross-platform research environments."""

from .terminal import console, print_header, print_success, print_error, print_info, print_warning, format_rc_file
from . import install
from . import system_info

__version__ = "0.1.0"
__all__ = ["console", "print_header", "print_success", "print_error", "print_info", "print_warning"]
