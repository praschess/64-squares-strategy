#!/usr/bin/env bash
set -euo pipefail
if [ $# -ne 1 ]; then echo "Usage: $0 <Lambda Function URL>"; exit 1; fi
python3 - "$1" <<'PY'
from pathlib import Path
import sys
url=sys.argv[1]
p=Path('js/chatbot.js')
p.write_text(p.read_text().replace('REPLACE_WITH_AWS_LAMBDA_FUNCTION_URL',url))
print('Configured',p,'with',url)
PY
