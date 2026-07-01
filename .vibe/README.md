# Vibe Configuration Files

This directory contains custom Vibe CLI configuration files that can be shared across multiple machines.

## Structure

```
.vibe/
├── prompts/                    # Custom agent prompts in Markdown
│   ├── code-architect.md       # Architecture design guidelines
│   ├── code-explorer.md        # Codebase exploration guidelines
│   └── code-reviewer.md        # Code review guidelines
├── agents/                    # Custom subagent configurations in TOML
│   ├── code-architect.toml     # Architecture subagent config
│   ├── code-explorer.toml     # Explorer subagent config
│   └── code-reviewer.toml      # Reviewer subagent config
├── skills/                    # Custom skills
│   └── feature-dev/            # Feature development workflow skill
│       └── SKILL.md            # Skill definition and workflow
├── install.sh                 # Installation script
├── uninstall.sh               # Uninstallation script
└── README.md                  # This file
```

## Installation

To install these configurations to your `~/.vibe` directory:

```bash
# Method 1: Run the install script
./.vibe/install.sh

# Method 2: Manual installation
mkdir -p ~/.vibe/{prompts,agents,skills}
cp .vibe/prompts/*.md ~/.vibe/prompts/
cp .vibe/agents/*.toml ~/.vibe/agents/
cp -r .vibe/skills/* ~/.vibe/skills/
```

After installation, restart your Vibe CLI for changes to take effect.

## Uninstallation

To remove these custom configurations:

```bash
./.vibe/uninstall.sh
```

## Files Description

### Prompts

- **code-architect.md**: Defines the behavior for the architecture design subagent. Focuses on proposing multiple implementation approaches with trade-offs.
- **code-explorer.md**: Guides the exploration subagent to understand codebase patterns and trace execution paths.
- **code-reviewer.md**: Instructs the review subagent to check for bugs, security issues, convention violations, and missing error handling.

### Agents

- **code-architect.toml**: Configuration for the architecture subagent with read-only tools and architectural design focus.
- **code-explorer.toml**: Configuration for the exploration subagent with tools for codebase analysis.
- **code-reviewer.toml**: Configuration for the review subagent with tools for code inspection.

### Skills

- **feature-dev/SKILL.md**: Complete feature development workflow skill that orchestrates the 7-phase development process using the subagents.

## Development

To add new custom configurations:

1. Create the appropriate file in the corresponding directory
2. Test locally by copying to `~/.vibe/`
3. Commit the changes to the repository
4. Run `./.vibe/install.sh` on target machines

## Usage on Remote Machines

1. Clone this repository on the remote machine
2. Run `./.vibe/install.sh` to install configurations
3. Restart Vibe CLI

The configurations will be automatically available to your Vibe installation.