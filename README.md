# server_config

> Standard configuration tools for research environments across Linux, MacOS, and Windows

A centralized repository for managing a consistent set of utilities across different research computers and servers. This repository uses [Pixi](https://pixi.sh) for cross-platform package management and [Rich](https://github.com/Textualize/rich) for beautiful terminal output.

## Features

- **Cross-platform support**: Works on Linux, MacOS, and Windows
- **Pixi package management**: Unified dependency management across all platforms
- **Rich terminal output**: Beautiful, informative console output
- **Idempotent installation**: Safe to run multiple times
- **Tool management**: Install, update, and check tool availability

## Quick Start

### Prerequisites

- Git
- Curl (for installing Pixi)
- Python >= 3.8 (for the configuration scripts)

### Installation

#### Method 1: Using the Install Script (Recommended)

```bash
# Clone the repository
git clone https://github.com/daw538/server_config.git
cd server_config

# Run the installation (installs pixi, then global tools)
./install.sh
```

#### Method 2: Manual Installation

```bash
# 1. Install Pixi (if not already installed)
curl -fsSL https://pixi.sh/install.sh | sh

# 2. Clone this repository
git clone https://github.com/daw538/server_config.git
cd server_config

# 3. Install global tools using Pixi
pixi global install dust duf bat

# 4. Sync the project environment
pixi sync
```

#### Method 3: Sourcing the Script (For Current Session)

```bash
# Source the install script to add tools to your current session
source install.sh
```

## Usage

### Python CLI

```bash
# Display system information
python -m server_config info
python -m server_config info --json  # JSON output

# Check which tools are installed
python -m server_config check

# Install tools
python -m server_config install all
python -m server_config install all --force  # Force reinstall
python -m server_config install tool dust   # Install specific tool
```

### Pixi Commands

```bash
# Install a specific tool globally
pixi global install dust

# List globally installed tools
pixi global list

# Sync the project environment
pixi sync

# Run a task defined in pixi.toml
pixi run system_info
pixi run install_all
```

### Bash Script

```bash
# Run full setup (pixi + tools)
./install.sh

# Source to add to current environment
source install.sh

# Check built-in functions
install_pixi     # Install or verify pixi
install_tools_pixi  # Install all tools via pixi
```

## Configuration

### `pixi.toml`

The main configuration file defines:

- **Project metadata**: Name, version, authors
- **Platform support**: Linux, MacOS, Windows architectures
- **Dependencies**: Core packages (rich, click, platformdirs)
- **Global tools**: dust, duf, bat configured as global pixi tools
- **Tasks**: Common operations like `install_all`, `system_info`
- **Development dependencies**: For working on this project

### Adding New Tools

To add a new tool to the configuration:

1. **Edit `server_config/install.py`**:
   ```python
   TOOLS_CONFIG["new_tool"] = {
       "description": "Tool description",
       "priority": 1,  # Lower = higher priority
       "install": {
           "pixi": "pixi global install new_tool",
           "brew": "brew install new_tool",
           "apt": "sudo apt install new_tool",
       },
       "check": "new_tool --version",
   }
   ```

2. **Add to pixi.toml** (if it should be managed globally):
   ```toml
   [tool.pixi.global-tools]
   new_tool = { from = "new_tool" }
   ```

## Project Structure

```
server_config/
├── pixi.toml              # Pixi project configuration
├── install.sh             # Main installation script
├── README.md              # Documentation
├── .gitignore             # Git ignore rules
└── server_config/         # Python package
    ├── __init__.py        # Package initialization
    ├── __main__.py        # Module entry point
    ├── cli.py             # Main CLI commands
    ├── install.py         # Tool installation logic
    ├── system_info.py     # System detection and info
    └── terminal.py        # Rich-based terminal utilities
```

## Tools Included

### Core Tools (Installed Globally)

- **`dust`**: A more powerful `du` alternative for disk usage analysis
- **`duf`**: Disk usage analyzer with pretty output
- **`bat`**: A `cat(1)` clone with syntax highlighting and Git integration

### Development Tools

- **`pixi`**: The package manager used by this project
- **`rich`**: Beautiful terminal formatting
- **`click`**: Command-line interface library
- **`platformdirs`**: Cross-platform application directory handling

## Cross-Platform Support

The configuration automatically detects the operating system and uses appropriate installation methods:

- **Linux**: Uses `apt`/`yum` or system-specific package managers
- **MacOS**: Uses `brew` where available
- **Windows**: Uses PowerShell scripts and Windows-specific tools
- **All platforms**: Prefers `pixi global install` when Pixi is available

## Environment Variables

- `PIXI_HOME`: Pixi installation directory (default: `~/.pixi`)
- `PATH`: Includes `~/.pixi/bin` for global tools

## Customization

### For Different Servers

Create environment-specific configurations by:

1. **Environment files**: Create `.env` files for different servers
2. **Custom tasks**: Add server-specific tasks in `pixi.toml`
3. **Conditional installation**: Modify installation scripts for server-specific requirements

### For Different Users

- Clone this repository to each user's home directory
- Customize `pixi.toml` per user needs
- Use different branches for different configurations

## Troubleshooting

### Common Issues

```bash
# Pixi not found
# Make sure pixi is in your PATH
export PATH="$HOME/.pixi/bin:$PATH"

# Tools not available
# Check if tools are installed globally
pixi global list

# Installation failures
# Run with verbose output
python -m server_config install all --verbose

# Missing dependencies
# Install required system tools first
# On Ubuntu/Debian: sudo apt install git curl
# On MacOS: brew install git curl
# On CentOS/RHEL: sudo yum install git curl
```

### Debug Mode

```bash
# Enable debug output
PIXI_DEBUG=true python -m server_config info
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [Pixi](https://pixi.sh) - Cross-platform package management
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal formatting
- [Click](https://click.palletsprojects.com/) - Command-line interface library
- All the amazing open-source tools included in this configuration
