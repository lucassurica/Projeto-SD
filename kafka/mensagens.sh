#!/usr/bin/env bash
# Mensageiro Kafka.  Terminal 1: ./mensagens.sh servidor   |   Terminal 2: ./mensagens.sh cliente
cd "$(dirname "$0")"
T=""; [ -t 0 ] || T="-T"
docker compose up -d --build kafka </dev/null >/dev/null 2>&1
until docker compose exec -T kafka /opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092 </dev/null >/dev/null 2>&1; do sleep 1; done
case "$1" in
  servidor) docker compose run --rm $T --build client python -u demos/chat_servidor.py ;;
  cliente)  docker compose run --rm $T --build client python -u demos/chat_cliente.py ;;
  *) echo "uso: $0 servidor|cliente"; exit 1 ;;
esac
