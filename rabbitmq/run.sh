#!/usr/bin/env bash
# Executa as demos de RabbitMQ.  Uso: ./run.sh [--auto] [numero-da-demo ...]
#   sem argumentos  -> todas, esperando ENTER entre elas (bom para gravar o vídeo)
#   --auto          -> sem pausas
set -e
cd "$(dirname "$0")"
AUTO=0; [ "$1" = "--auto" ] && { AUTO=1; shift; }
PY="docker compose run --rm --no-TTY client python"

pausa() { [ $AUTO = 1 ] || { echo; read -rp ">>> ENTER para continuar..." _; }; }
esperar_broker() { until docker compose exec -T rabbitmq rabbitmq-diagnostics -q ping >/dev/null 2>&1; do sleep 1; done; }

docker compose up -d --build rabbitmq >/dev/null
docker compose build client >/dev/null
echo "Painel de gerenciamento: http://localhost:15672  (guest/guest)"
esperar_broker

demo() { # $1=numero $2=arquivo
  if [ $# -ge 1 ] && { [ -z "$SEL" ] || [[ " $SEL " == *" $1 "* ]]; }; then return 0; else return 1; fi
}
SEL="$*"
rodar() { demo "$1" && { $PY demos/$2 ${3:-}; pausa; } || true; }

rodar 1 01_direct.py
rodar 2 02_fanout.py
rodar 3 03_topic.py
rodar 4 04_headers.py
rodar 5 05_round_robin.py
rodar 6 06_round_robin_ponderado.py
if demo 7; then
  $PY demos/07_persistencia.py publicar
  echo; echo ">>> Reiniciando o broker RabbitMQ (docker compose restart rabbitmq)..."
  docker compose restart rabbitmq >/dev/null; esperar_broker
  $PY demos/07_persistencia.py verificar
  pausa
fi
rodar 8 08_confirmacoes.py
rodar 9 09_prioridade.py
echo; echo "Fim. Encerrar: docker compose down -v"
