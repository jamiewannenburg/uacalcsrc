#!/usr/bin/env bash
#
# Cloud Agent install script for the UACalc Rust/Python/Java project.
#
# Idempotent: safe to run repeatedly and against cached/partial state.
# Prepares three toolchains that the repository needs end to end:
#   * Rust   - core library + `uacalc` binary, and the PyO3 binding crate
#   * Java   - reference "ground truth" wrappers used by comparison tests
#   * Python - maturin-built `uacalc_lib` extension + test dependencies
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

# --- Build Java reference wrappers -----------------------------------------
# `compile-wrappers` also compiles the full Java sources it depends on. These
# wrappers are invoked as ground truth by the Rust/Python comparison tests.
ant compile-wrappers

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
