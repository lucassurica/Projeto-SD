#!/usr/bin/env bash
# Demonstração gRPC: servidor e cliente Python, ambos gerados a partir do mesmo .proto.
set -e
cd "$(dirname "$0")"

echo ">>> Subindo o servidor gRPC (Python)..."
docker compose up -d --build server

echo; echo "################ CLIENTE ################"
docker compose run --rm --build client


echo; echo "################ LOG DO SERVIDOR ################"
docker compose logs --no-log-prefix server

echo; echo "(para encerrar: docker compose down)"
