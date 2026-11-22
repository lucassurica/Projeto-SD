# Apache Kafka - confluent-kafka

    docker compose up -d
    pip install -r requirements.txt
    python criar_topico.py                 # topico 'mensagens' com 3 particoes
    python consumidor.py g1                # terminal 1 (rode tambem em 2 terminais com g1 -> particoes divididas)
    python produtor.py                     # terminal 2
    python consumidor.py g2                # grupo novo le tudo de novo (replay)

Comparacao com RabbitMQ: ver KAFKA_vs_RABBITMQ.md
