#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
python3 -m PyInstaller --noconfirm W4GNS-General-Logger.spec
