#!/usr/bin/env bash
#
# Cloud Agent install script for the UACalc Rust/Python/Java project.
#
# Idempotent: safe to run repeatedly and against cached/partial state.
# Prepares the toolchains that the repository needs end to end:
#   * Rust   - core library + `uacalc` binary, and the PyO3 binding crate
#   * Java   - reference "ground truth" wrappers + uacalc.jar used by tests
#   * Python - maturin-built `uacalc_lib` extension + test dependencies
#   * Jython - Java-backed Python used by the tests/parity golden checks
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# --- System packages -------------------------------------------------------
# Ant builds the Java wrappers; python venv/dev headers are needed to build
# an isolated environment for the maturin-built extension module.
sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends ant python3-venv python3-dev

# --- Rust toolchain --------------------------------------------------------
# The default base image can pin an older Rust that cannot resolve some
# edition-2024 transitive dependencies. Use the current stable toolchain.
rustup default stable

# --- Build Rust workspace --------------------------------------------------
# Compiles the core `uacalc` crate and the `uacalc` binary.
cargo build

# --- Build Java reference wrappers + uacalc.jar ----------------------------
# `dist` compiles the full Java sources, builds the command-line wrappers
# (ground truth for the Rust/Python comparison tests), and packages
# `jars/uacalc.jar`. The jar is required on Jython's CLASSPATH by the
# `tests/parity` golden checks, which otherwise skip.
ant dist

# --- Jython (tests/parity golden checks) -----------------------------------
# The parity tests invoke `jython` to exercise the Java reference surface and
# compare it against the CPython bindings; they skip when `jython` is not on
# PATH. Install Jython 2.7.3 and expose it via a symlink so every shell (and
# `shutil.which`) finds it without mutating shell profiles.
JYTHON_HOME="$HOME/jython"
if [ ! -x "$JYTHON_HOME/bin/jython" ]; then
  curl -fsSL -o /tmp/jython-installer.jar \
    "https://repo1.maven.org/maven2/org/python/jython-installer/2.7.3/jython-installer-2.7.3.jar"
  # Silent install (-s), prefix (-d), full standard install with cached stdlib (-t standard).
  java -jar /tmp/jython-installer.jar -s -d "$JYTHON_HOME" -t standard
fi
sudo ln -sf "$JYTHON_HOME/bin/jython" /usr/local/bin/jython
jython --version

# --- Python environment ----------------------------------------------------
# Isolated venv holding the maturin-built `uacalc_lib` extension and the
# project's test dependencies. Activate with `source .venv/bin/activate`.
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install maturin
maturin develop
pip install -e ".[test]"

echo "UACalc environment install complete."
