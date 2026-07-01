#!/bin/bash

# Vibe Configuration Installer
# This script copies custom Vibe prompts, agents, and skills
# from this repository to the user's ~/.vibe directory

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VIBE_DIR="$HOME/.vibe"

echo -e "${BLUE}==> Vibe Configuration Installer${NC}"
echo -e "${BLUE}Script directory: $SCRIPT_DIR${NC}"
echo -e "${BLUE}Target directory: $VIBE_DIR${NC}"
echo

# Check if we're in the right location
if [ ! -f "$SCRIPT_DIR/prompts/code-architect.md" ] && [ ! -f "$SCRIPT_DIR/prompts/code-explorer.md" ]; then
    echo -e "${RED}Error:Cannot find Vibe config files in $SCRIPT_DIR${NC}"
    echo -e "${RED}Please run this script from the repository root or .vibe directory${NC}"
    exit 1
fi

# Check if ~/.vibe exists, create if not
if [ ! -d "$VIBE_DIR" ]; then
    echo -e "${YELLOW}Creating ~/.vibe directory...${NC}"
    mkdir -p "$VIBE_DIR"
    echo -e "${GREEN}✓ Created ~/.vibe directory${NC}"
fi

# Create target directories
for dir in prompts agents skills; do
    if [ ! -d "$VIBE_DIR/$dir" ]; then
        echo -e "${YELLOW}Creating ~/.vibe/$dir directory...${NC}"
        mkdir -p "$VIBE_DIR/$dir"
        echo -e "${GREEN}✓ Created ~/.vibe/$dir directory${NC}"
    fi
done

# Copy prompts
echo -e "${YELLOW}Copying custom prompts...${NC}"
if [ -d "$SCRIPT_DIR/prompts" ]; then
    for prompt_file in "$SCRIPT_DIR"/prompts/*.md; do
        filename=$(basename "$prompt_file")
        cp "$prompt_file" "$VIBE_DIR/prompts/"
        echo -e "${GREEN}✓ Copied $filename to ~/.vibe/prompts/${NC}"
    done
else
    echo -e "${YELLOW}No prompts directory found, skipping...${NC}"
fi

# Copy agents
echo -e "${YELLOW}Copying custom agents...${NC}"
if [ -d "$SCRIPT_DIR/agents" ]; then
    for agent_file in "$SCRIPT_DIR"/agents/*.toml; do
        filename=$(basename "$agent_file")
        cp "$agent_file" "$VIBE_DIR/agents/"
        echo -e "${GREEN}✓ Copied $filename to ~/.vibe/agents/${NC}"
    done
else
    echo -e "${YELLOW}No agents directory found, skipping...${NC}"
fi

# Copy skills
echo -e "${YELLOW}Copying custom skills...${NC}"
if [ -d "$SCRIPT_DIR/skills" ]; then
    # Copy each skill directory recursively
    for skill_dir in "$SCRIPT_DIR"/skills/*/; do
        skill_name=$(basename "$skill_dir")
        skill_target="$VIBE_DIR/skills/$skill_name"
        
        # Create skill directory if it doesn't exist
        mkdir -p "$skill_target"
        
        # Copy all files in the skill directory
        for skill_file in "$skill_dir"*; do
            filename=$(basename "$skill_file")
            cp "$skill_file" "$skill_target/"
            echo -e "${GREEN}✓ Copied $filename to ~/.vibe/skills/$skill_name/${NC}"
        done
    done
else
    echo -e "${YELLOW}No skills directory found, skipping...${NC}"
fi

# Optional: Copy config.toml if it exists in the repo
if [ -f "$SCRIPT_DIR/config.toml" ]; then
    echo -e "${YELLOW}Found config.toml in repo...${NC}"
    if [ -f "$VIBE_DIR/config.toml" ]; then
        echo -e "${YELLOW}Backing up existing config.toml to config.toml.bak...${NC}"
        cp "$VIBE_DIR/config.toml" "$VIBE_DIR/config.toml.bak"
    fi
    echo -e "${YELLOW}Do you want to overwrite ~/.vibe/config.toml? (y/n): ${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        cp "$SCRIPT_DIR/config.toml" "$VIBE_DIR/config.toml"
        echo -e "${GREEN}✓ Copied config.toml to ~/.vibe/${NC}"
    else
        echo -e "${YELLOW}Skipped copying config.toml${NC}"
    fi
fi

echo
echo -e "${BLUE}==> Installation Summary${NC}"
echo -e "${GREEN}Custom Vibe configurations have been installed to ~/.vibe/${NC}"
echo

# Show what was installed
echo -e "${BLUE}Installed prompts:${NC}"
ls -la "$VIBE_DIR/prompts/" 2>/dev/null || echo "No prompts installed"

echo
echo -e "${BLUE}Installed agents:${NC}"
ls -la "$VIBE_DIR/agents/" 2>/dev/null || echo "No agents installed"

echo
echo -e "${BLUE}Installed skills:${NC}"
ls -la "$VIBE_DIR/skills/" 2>/dev/null || echo "No skills installed"

echo
echo -e "${GREEN}Installation complete!${NC}"
echo -e "${YELLOW}You may need to restart your Vibe CLI for changes to take effect.${NC}"