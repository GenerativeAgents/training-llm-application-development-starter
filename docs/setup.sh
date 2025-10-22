#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

if [ "$(whoami)" != "ubuntu" ]; then
  echo "This script must be run as ubuntu user" >&2
  exit 1
fi

# ソースコードのダウンロード
cd /home/ubuntu/environment
if [ ! -d "training-llm-application-development-starter" ]; then
  git clone https://github.com/GenerativeAgents/training-llm-application-development-starter.git
fi
cd training-llm-application-development-starter

# uvのインストール
curl -LsSf https://astral.sh/uv/0.4.14/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
uv --version

# PythonとPythonパッケージのインストール
uv sync
uv run python --version

# langchainリポジトリのclone
if [ ! -d "./tmp/langchain-docs" ]; then
  git clone --depth 1 https://github.com/langchain-ai/docs.git ./tmp/langchain-docs
fi

# Visual Studio Codeの拡張機能のインストール
recommendations=(
  "charliermarsh.ruff"
  "ms-python.mypy-type-checker"
  "ms-toolsai.jupyter"
)
for recommendation in "${recommendations[@]}"; do
  code-server --install-extension "${recommendation}" --force
done
