#!/usr/bin/env bash
# Demonstração REST: servidor FastAPI + cliente Python + curl (cliente "agnóstico" de linguagem).
set -e
cd "$(dirname "$0")"
K="X-API-Key: segredo-sd"

echo ">>> Subindo o servidor REST..."
docker compose up -d --build server
until curl -sf localhost:8000/saude >/dev/null; do sleep 0.5; done

echo; echo "################ CLIENTE PYTHON (requests) ################"
docker compose run --rm --build client

echo; echo "################ CURL: qualquer cliente HTTP fala com a API ################"
set -x
curl -si -H "$K" localhost:8000/v1/produtos/1 | head -12
curl -s  -H "$K" -H "Accept: text/csv" "localhost:8000/v1/produtos?limite=3"
curl -si -X OPTIONS localhost:8000/v1/produtos | head -4
set +x
echo; echo "Swagger UI: http://localhost:8000/docs   |   encerrar: docker compose down"
