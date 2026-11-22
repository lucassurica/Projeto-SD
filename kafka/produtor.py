"""Envia 9 mensagens. A CHAVE define a particao: mesma chave -> mesma particao (ordem preservada)."""
from confluent_kafka import Producer

p = Producer({"bootstrap.servers": "localhost:9092"})


def relatorio(err, msg):
    if err:
        print("erro:", err)
    else:
        print(f"enviada '{msg.value().decode()}' -> particao {msg.partition()} offset {msg.offset()}")


for i in range(1, 10):
    chave = f"usuario{i % 3}"
    p.produce("mensagens", key=chave, value=f"mensagem {i} ({chave})", callback=relatorio)
p.flush()
