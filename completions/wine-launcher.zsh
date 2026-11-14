# Wine Launcher - Zsh Completion
# Install: fpath=(/path/to/completions $fpath) && compinit
# Or copy to /usr/share/zsh/site-functions/_wine-launcher

#compdef wine-launcher

_wine_launcher() {
    local -a options
    options=(
        '--version[Show version and exit]'
        '--help[Show help and exit]'
    )

    _arguments -C -s "${options[@]}" && return 0
}

_wine_launcher "$@"