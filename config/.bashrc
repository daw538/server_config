# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions

# --- Tool initialization (requires PATH to be set first) ---
export PATH="/home/links/dw592/.pixi/bin:$PATH"
eval "$(pixi completion --shell bash)"
eval "$(starship init bash)"


# --- Environment settings ---
export EDITOR=nano
export GREP_OPTIONS='--color=auto'
export HISTSIZE=100000
export HISTFILESIZE=1000000


eval "$(dircolors ~/.dircolors 2>/dev/null)"
#source /home/links/dw592/.config/broot/launcher/bash/br
