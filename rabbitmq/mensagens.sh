#!/usr/bin/env bash
# Mensageiro RabbitMQ.  Terminal 1: ./mensagens.sh servidor   |   Terminal 2: ./mensagens.sh cliente
cd "$(dirname "$0")"
T=""; [ -t 0 ] || T="-T"
docker compose up -d --build rabbitmq >/dev/null 2>&1
case "$1" in
  servidor) docker compose run --rm $T --build client python -u demos/chat_servidor.py ;;
  cliente)  docker compose run --rm $T --build client python -u demos/chat_cliente.py ;;
  *) echo "uso: $0 servidor|cliente"; exit 1 ;;
esac
