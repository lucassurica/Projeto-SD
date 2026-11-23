# RabbitMQ (AMQP) - pika

    docker compose up -d        # painel: http://localhost:15672 (guest/guest)
    pip install -r requirements.txt
    # rode docker compose up -d novamente caso não tenha funcionado na primeira vez

Cada demo usa 2+ terminais: primeiro o(s) consumidor(es), depois o produtor.

## 1. Roteamento (4 tipos de exchange)
    python roteamento_consumidor.py direct erro          ; python roteamento_produtor.py direct
    python roteamento_consumidor.py fanout               ; python roteamento_produtor.py fanout
    python roteamento_consumidor.py topic "*.erro"       ; python roteamento_produtor.py topic
    python roteamento_consumidor.py headers formato=pdf  ; python roteamento_produtor.py headers

## 2. Balanceamento de carga
# Round-robin:
    python balanceamento_consumidor.py A     (terminal 1)
    python balanceamento_consumidor.py B     (terminal 2)
    python balanceamento_produtor.py 12      (terminal 3)  -> A e B recebem 6 cada
# Round-robin ponderado (A com peso 3, B com peso 1 -> 3:1):
    python balanceamento_consumidor.py A --peso 3
    python balanceamento_consumidor.py B --peso 1
    python balanceamento_produtor.py 12
# Fair dispatch (por disponibilidade) Compare rodando antes sem --prefetch, com os mesmos tempos.
    python balanceamento_consumidor.py A --prefetch 1 --tempo 0.1    (terminal 1, rapido)
    python balanceamento_consumidor.py B --prefetch 1 --tempo 1.0    (terminal 2, lento)
    python balanceamento_produtor.py 12                              (terminal 3)

## 3. Persistente x transiente
    python persistencia.py enviar ; docker compose restart rabbitmq ; python persistencia.py ler

## 4. Com e sem confirmacao
# O consumidor so le o que esta na fila: rode o produtor ANTES de cada consumidor, senao ele fica
# so em "aguardando...". Feche (Ctrl+C) consumidores antigos antes de recomecar.

    python confirmacao_produtor.py                      # publisher confirms: coloca 5 pedidos na fila
    python confirmacao_consumidor.py auto --falhar      # recebe 1, 2 e 3; cai no 3 (auto-ack)
    python confirmacao_produtor.py                      # enche a fila de novo
    python confirmacao_consumidor.py manual --falhar    # confirma (ack) 1 e 2; cai no 3 sem ack
    python confirmacao_consumidor.py manual             # recebe 3, 4 e 5 com redelivered=True; encerre com
                                                        # Ctrl + C 

## 5. Prioridade
    python prioridade.py enviar ; python prioridade.py ler
