#!/usr/bin/env bash
set -euxo pipefail

PYODIDE_VERSION=${PYODIDE_VERSION:-0.27.7}

# 1. Clean previous artefacts
rm -rf .venv-pyodide vendor

# 2. Make sure pyodide-cli is available through uv's toolchain
uv tool install --with pyodide-build --with pip pyodide-cli --python 3.12

# 3. Install the cross-build toolchain (Wasm sysroot, etc.)
pyodide xbuildenv install "${PYODIDE_VERSION}"

# 4. Create the virtualenv that uv will work against
pyodide venv .venv-pyodide

# 5. Resolve *binary-compatible* wheels first (Pyodide index),
#    falling back to PyPI for pure-Python packages
uv export \
  --python .venv-pyodide \
  --index https://pyodide.astral.sh/${PYODIDE_VERSION} \
  | uv pip sync \
      --no-installer-metadata \
      --no-compile-bytecode \
      --only-binary :all: \
      --index-strategy unsafe-best-match \
      --target vendor \
      --python .venv-pyodide \
      --index https://pyodide.astral.sh/${PYODIDE_VERSION} \
      -

# 6. Add our source code to vendor directory
cp -r src/sefaria_mcp vendor/

echo "✅  Build artefacts are in ./vendor – ready for 'wrangler publish'"
