#!/bin/bash

# Vibe Configuration Uninstaller
# This script removes custom Vibe prompts, agents, and skills
# from the user's ~/.vibe directory

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

VIBE_DIR="$HOME/.vibe"

echo -e "${BLUE}==> Vibe Configuration Uninstaller${NC}"
echo -e "${BLUE}Target directory: $VIBE_DIR${NC}"
echo

# Confirm before uninstalling
echo -e "${RED}WARNING: This will remove custom Vibe configurations from ~/.vibe/${NC}"
echo -e "${RED}The following will be removed:${NC}"
echo

# Show what will be removed
if [ -d "$VIBE_DIR/prompts" ]; then
    echo -e "${YELLOW}Prompts:${NC}"
    ls "$VIBE_DIR/prompts/" 2>/dev/null | sed 's/^/  /' || echo "  (none)"
fi

if [ -d "$VIBE_DIR/agents" ]; then
    echo -e "${YELLOW}Agents:${NC}"
    ls "$VIBE_DIR/agents/" 2>/dev/null | sed 's/^/  /' || echo "  (none)"
fi

if [ -d "$VIBE_DIR/skills" ]; then
    echo -e "${YELLOW}Skills:${NC}"
    find "$VIBE_DIR/skills/" -type f 2>/dev/null | sed 's|^.*/|  |' || echo "  (none)"
fi

echo
echo -e "${RED}Do you want to continue with uninstallation? (y/n): ${NC}"
read -r response

if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${YELLOW}Uninstallation cancelled.${NC}"
    exit 0
fi

# Remove prompts
echo -e "${YELLOW}Removing custom prompts...${NC}"
if [ -d "$VIBE_DIR/prompts" ]; then
    rm -rf "$VIBE_DIR/prompts"
    mkdir -p "$VIBE_DIR/prompts"  # Recreate empty directory
    echo -e "${GREEN}✓ Removed custom prompts${NC}"
fi

# Remove agents
echo -e "${YELLOW}Removing custom agents...${NC}"
if [ -d "$VIBE_DIR/agents" ]; then
    rm -rf "$VIBE_DIR/agents"
    mkdir -p "$VIBE_DIR/agents"  # Recreate empty directory
    echo -e "${GREEN}✓ Removed custom agents${NC}"
fi

# Remove skills
echo -e "${YELLOW}Removing custom skills...${NC}"
if [ -d "$VIBE_DIR/skills" ]; then
    rm -rf "$VIBE_DIR/skills"
    mkdir -p "$VIBE_DIR/skills"  # Recreate empty directory
    echo -e "${GREEN}✓ Removed custom skills${NC}"
fi

echo
echo -e "${GREEN}Uninstallation complete!${NC}"
echo -e "${YELLOW}You may need to restart your Vibe CLI for changes to take effect.${NC}"