#!/bin/bash
set -euo pipefail
$(poetry env acticate)

exec "$@"
