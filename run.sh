#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Run main module inside the virtual environment
.venv/bin/python -m app_launcher.main "$@"
