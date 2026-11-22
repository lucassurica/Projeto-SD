# RabbitMQ (AMQP) - pika

    docker compose up -d        # painel: http://localhost:15672 (guest/guest)
    pip install -r requirements.txt

Cada demo usa 2+ terminais: primeiro o(s) consumidor(es), depois o produtor.

## 1. Roteamento (4 tipos de exchange)
    python roteamento_consumidor.py direct erro          ; python roteamento_produtor.py direct
    python roteamento_consumidor.py fanout               ; python roteamento_produtor.py fanout
    python roteamento_consumidor.py topic "*.erro"       ; python roteamento_produtor.py topic
    python roteamento_consumidor.py headers formato=pdf  ; python roteamento_produtor.py headers

## 2. Balanceamento de carga
Round-robin:
    python balanceamento_consumidor.py A     (terminal 1)
    python balanceamento_consumidor.py B     (terminal 2)
    python balanceamento_produtor.py 12      (terminal 3)  -> A e B recebem 6 cada
Round-robin ponderado (A com peso 3, B com peso 1 -> 3:1):
    python balanceamento_consumidor.py A --peso 3
    python balanceamento_consumidor.py B --peso 1
    python balanceamento_produtor.py 12
Fair dispatch (por disponibilidade): adicione --prefetch 1 e use --tempo diferentes.

## 3. Persistente x transiente
    python persistencia.py enviar ; docker compose restart rabbitmq ; python persistencia.py ler

## 4. Com e sem confirmacao
    python confirmacao_produtor.py                      # publisher confirms
    python confirmacao_consumidor.py auto --falhar      # msg 3 se perde
    python confirmacao_consumidor.py manual --falhar    # msg 3 e reentregue (redelivered=True)
    python confirmacao_consumidor.py manual             # rode de novo para consumir a pendente

## 5. Prioridade
    python prioridade.py enviar ; python prioridade.py ler
