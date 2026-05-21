#!/bin/bash

PREF_FILE="$HOME/.config/google-chrome/Default/Preferences"

if [ ! -f "$PREF_FILE" ]; then
    echo "No se encontró el archivo Preferences de Google Chrome"
    exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
    echo "jq no está instalado. Instálalo con: sudo apt install jq"
    exit 1
fi

TMP_FILE=$(mktemp)

jq '
.browser.startup.homepage = "https://www.youtube.com" |
.browser.startup.homepage_is_newtabpage = false |
.session.startup_urls = ["https://www.youtube.com"] |
.session.restore_on_startup = 4
' "$PREF_FILE" > "$TMP_FILE" && mv "$TMP_FILE" "$PREF_FILE"

echo "Homepage configurada a YouTube en Google Chrome"