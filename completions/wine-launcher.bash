# Wine Launcher - Bash Completion
# Install: source /path/to/wine-launcher.bash
# Or copy to /etc/bash_completion.d/ or ~/.local/share/bash-completion/completions/

_wine_launcher() {
    local cur prev opts bottles
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main options
    local main_opts="--version --help"

    # If completing first argument after command
    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=($(compgen -W "${main_opts}" -- "${cur}"))
        return 0
    fi

    # No subcommands, just options
    COMPREPLY=($(compgen -W "${main_opts}" -- "${cur}"))
}

complete -F _wine_launcher wine-launcher