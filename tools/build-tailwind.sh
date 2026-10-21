#!/usr/bin/env bash
# Rebuild css/tailwind.css (replaces the old Tailwind CDN script).
# Pinned to 3.4.17, the version the CDN was serving, so output matches.
# Re-run after adding pages or new class names, then commit css/tailwind.css.
set -euo pipefail
cd "$(dirname "$0")/.."
npx -y tailwindcss@3.4.17 -c tools/tailwind/tailwind.config.js -i tools/tailwind/input.css -o css/tailwind.css --minify
