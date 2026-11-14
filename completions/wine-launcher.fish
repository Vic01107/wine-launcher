# Wine Launcher - Fish Completion
# Install: copy to ~/.config/fish/completions/wine-launcher.fish

complete -c wine-launcher -f -n "__fish_use_subcommand" \
    -l version -d "Show version and exit" \
    -l help -d "Show help and exit"