#!/usr/bin/env bash
# Executa as demos de Kafka.  Uso: ./run.sh [--auto] [numero-da-demo ...]
set -e
cd "$(dirname "$0")"
AUTO=0; [ "$1" = "--auto" ] && { AUTO=1; shift; }
SEL="$*"
PY="docker compose run --rm --no-TTY client python"
K="docker compose exec -T kafka /opt/kafka/bin"

pausa() { [ $AUTO = 1 ] || { echo; read -rp ">>> ENTER para continuar..." _; }; }
quer() { [ -z "$SEL" ] || [[ " $SEL " == *" $1 "* ]]; }

if quer 5; then docker compose --profile comparacao up -d --build kafka rabbitmq >/dev/null
else docker compose up -d --build kafka >/dev/null; fi
docker compose build client >/dev/null
until docker compose exec -T kafka /opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092 >/dev/null 2>&1; do sleep 1; done

quer 1 && { $PY demos/k1_particoes_chaves.py; echo
  echo "--- CLI do Kafka: kafka-topics.sh --describe ---"
  $K/kafka-topics.sh --bootstrap-server kafka:9092 --describe --topic pedidos; pausa; }
quer 2 && { $PY demos/k2_grupos_consumidores.py; pausa; }
quer 3 && { $PY demos/k3_replay_offsets.py; echo
  echo "--- CLI do Kafka: kafka-consumer-groups.sh --describe (offsets e LAG por grupo) ---"
  $K/kafka-consumer-groups.sh --bootstrap-server kafka:9092 --describe --all-groups 2>/dev/null | grep -E "GROUP|relatorios|antifraude" ; pausa; }
quer 4 && { $PY demos/k4_semanticas_entrega.py; pausa; }
quer 5 && { $PY demos/k5_comparacao_rabbitmq.py; pausa; }
echo; echo "Fim. Encerrar: docker compose --profile comparacao down -v"
