#!/usr/bin/env bash
# Mensageiro gRPC.  Terminal 1: ./mensagens.sh servidor   |   Terminal 2: ./mensagens.sh cliente
cd "$(dirname "$0")"
T=""; [ -t 0 ] || T="-T"
case "$1" in
  servidor) docker compose up --build server ;;
  cliente)  docker compose up -d --build server >/dev/null 2>&1
            docker compose run --rm $T --build client python -u mensagem_client.py ;;
  *) echo "uso: $0 servidor|cliente"; exit 1 ;;
esac
