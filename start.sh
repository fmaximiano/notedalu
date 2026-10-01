#!/bin/sh
set -eu

echo "=== Note da Lu: iniciando Streamlit ==="
echo "PORT=${PORT:-8501}"
exec streamlit run app.py \
  --server.address=0.0.0.0 \
  --server.port="${PORT:-8501}" \
  --server.headless=true
