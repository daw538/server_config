#!/bin/bash
#
# Server Configuration Install Script
# 
# Usage: ./install.sh              # Run installation directly
#        source install.sh         # Add to current session PATH
# 
# For full functionality, use the Python CLI:
#   python -m server_config install all
#   python -m server_config install --help
# 
# Tools: pixi, dust, duf, bat, htop, starship, vibe
#

set -euo pipefail

# Colors for output (compatible with most terminals)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Function to print messages with colors
print_header() {
    echo -e "${CYAN}${BOLD}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if running in a login shell or if pixi is in PATH
check_pixi() {
    if command -v pixi &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to install pixi if not present
install_pixi() {
    if check_pixi; then
        print_success "pixi is already installed"
        return 0
    fi
    
    print_info "Installing pixi..."
    local os_type
    os_type=$(uname -s | tr '[:upper:]' '[:lower:]')
    
    case "$os_type" in
        linux*|darwin*)
            # Unix-like systems (Linux, macOS)
            curl -fsSL https://pixi.sh/install.sh | sh
            ;;
        mingw*|msys*|cygwin*)
            # Windows via MSYS2/MinGW
            powershell -c "iwr -useb https://pixi.sh/install.ps1 | iex"
            ;;
        *)
            print_error "Unsupported OS: $os_type"
            return 1
            ;;
    esac
    
    # Add pixi to shell config if not already present
    if ! grep -q "pixi" ~/.bashrc 2>/dev/null && ! grep -q "pixi" ~/.zshrc 2>/dev/null; then
        print_info "Adding pixi to shell configuration..."
        local shell_config=""
        if [ -f ~/.bashrc ]; then
            shell_config="~/.bashrc"
        elif [ -f ~/.zshrc ]; then
            shell_config="~/.zshrc"
        fi
        
        if [ -n "$shell_config" ]; then
            echo "" >> "$shell_config"
            echo "# Added by server_config" >> "$shell_config"
            echo 'export PATH="$HOME/.pixi/bin:$PATH"' >> "$shell_config"
            echo 'export PIXI_HOME="$HOME/.pixi"' >> "$shell_config"
        fi
    fi
    
    # Source the config to make pixi available in current session
    if check_pixi; then
        print_success "pixi installed successfully"
        return 0
    else
        print_error "pixi installation failed"
        return 1
    fi
}

# Function to install all configured tools via pixi
install_tools_pixi() {
    print_header "Installing Tools via Pixi"
    
    # Navigate to the server_config directory
    local script_dir
    script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    
    # Install global tools using pixi
    local tools=("dust" "duf" "bat" "htop" "starship" "mistral-vibe")
    
    for tool in "${tools[@]}"; do
        if pixi global list | grep -q "$tool"; then
            print_success "$tool is already installed globally"
        else
            print_info "Installing $tool globally..."
            if pixi global install "$tool"; then
                print_success "$tool installed successfully"
            else
                print_error "Failed to install $tool"
            fi
        fi
    done
}

# Function to setup the environment
setup_environment() {
    print_header "Setting up server_config environment"
    
    local script_dir
    script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    
    # Install pixi first
    if ! install_pixi; then
        print_error "pixi installation failed, cannot continue"
        return 1
    fi
    
    # Sync pixi environment
    if [ -f "$script_dir/pixi.toml" ]; then
        print_info "Syncing pixi environment..."
        cd "$script_dir"
        if pixi sync; then
            print_success "Pixi environment synced"
        else
            print_warning "Pixi sync failed, but continuing..."
        fi
    fi
    
    # Install global tools
    install_tools_pixi
    
    # Configure starship prompt
    configure_starship
    
    print_info "Setup complete!"
    echo ""
    print_info "To use the installed tools, ensure pixi is in your PATH:"
    print_info "  export PATH=\"\$HOME/.pixi/bin:\$PATH\""
}

# Function to add server_config to PATH for tab completion
add_to_path() {
    local script_dir
    script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    
    # Add to PATH if not already present
    if [[ ":$PATH:" != *":$script_dir:"* ]]; then
        export PATH="$script_dir:$PATH"
    fi
    
    # Add pixi to PATH if not already present
    local pixi_bin="$HOME/.pixi/bin"
    if [ -d "$pixi_bin" ] && [[ ":$PATH:" != *":$pixi_bin:"* ]]; then
        export PATH="$pixi_bin:$PATH"
    fi
}

# Function to detect the current shell
detect_shell() {
    local shell=""
    
    # Check SHELL environment variable
    if [ -n "$SHELL" ]; then
        shell=$(basename "$SHELL")
        case "$shell" in
            bash|zsh|fish|sh|dash|csh|tcsh)
                echo "$shell"
                return 0
                ;;
        esac
    fi
    
    # Check for existing rc files
    if [ -f ~/.zshrc ]; then
        echo "zsh"
        return 0
    elif [ -f ~/.bashrc ]; then
        echo "bash"
        return 0
    elif [ -f ~/.config/fish/config.fish ]; then
        echo "fish"
        return 0
    fi
    
    # Default to bash
    echo "bash"
    return 0
}

# Function to get the rc file for a given shell
get_rc_file() {
    local shell="$1"
    case "$shell" in
        zsh)    echo "$HOME/.zshrc" ;;
        bash)   echo "$HOME/.bashrc" ;;
        fish)   echo "$HOME/.config/fish/config.fish" ;;
        sh|dash) echo "$HOME/.profile" ;;
        csh|tcsh) echo "$HOME/.cshrc" ;;
        *)      echo "$HOME/.bashrc" ;;
    esac
}

# Function to configure starship prompt
configure_starship() {
    # Check if starship is installed
    if ! command -v starship &> /dev/null; then
        print_info "starship not found, skipping shell configuration"
        return 0
    fi
    
    local shell
    shell=$(detect_shell)
    local rc_file
    rc_file=$(get_rc_file "$shell")
    
    # Define the init command for this shell
    local init_cmd=""
    case "$shell" in
        bash)   init_cmd='eval "$(starship init bash)"' ;;
        zsh)    init_cmd='eval "$(starship init zsh)"' ;;
        fish)   init_cmd='starship init fish | source' ;;
        *)      init_cmd='eval "$(starship init bash)"' ;;
    esac
    
    # Check if already configured
    if [ -f "$rc_file" ] && grep -qF "$init_cmd" "$rc_file" 2>/dev/null; then
        print_success "starship is already configured in $rc_file"
        return 0
    fi
    
    # Prompt user
    print_info "Starship prompt is installed but not yet configured for your shell."
    print_info "This adds a prompt with git status, directory, and other context to your terminal."
    read -p "Add starship initialization to $rc_file? [Y/n]: " response
    
    # Default to yes
    response=${response:-Y}
    
    if [[ "${response,,}" =~ ^(yes|y) ]]; then
        # Create backup
        local backup_file="${rc_file}.starship_bak_$(date +%Y%m%d_%H%M%S)"
        if [ -f "$rc_file" ]; then
            cp "$rc_file" "$backup_file"
            print_info "Created backup: $backup_file"
        fi
        
        # Add the initialization
        echo "" >> "$rc_file"
        echo "# Starship prompt initialization (added by server_config)" >> "$rc_file"
        echo "$init_cmd" >> "$rc_file"
        
        print_success "starship initialization added to $rc_file"
        print_info "Start a new shell session or run 'source $rc_file' to activate it."
        return 0
    else
        print_info "Skipped starship shell configuration."
        print_info "To enable later, add this to your $rc_file:"
        print_info "  $init_cmd"
        return 0
    fi
}

# Main execution
main() {
    # Detect how the script was called
    if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
        # Script was executed directly
        setup_environment
        exit 0
    else
        # Script was sourced
        print_header "server_config environment activated"
        add_to_path
        print_success "Commands are now available"
        if ! check_pixi; then
            print_warning "pixi is not available. Run 'install_pixi' to install it."
        fi
    fi
}

# Run main function
main "$@"
