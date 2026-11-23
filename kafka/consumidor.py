"""Uso: python consumidor.py <grupo>
 - Mesmo grupo em varios terminais: as particoes sao DIVIDIDAS entre eles (balanceamento).
 - Grupo novo: recebe TUDO desde o inicio (replay) - a mensagem nao some apos ser lida."""
import sys
from confluent_kafka import Consumer

grupo = sys.argv[1] if len(sys.argv) > 1 else "grupo1"
c = Consumer({"bootstrap.servers": "localhost:9092", "group.id": grupo,
              "auto.offset.reset": "earliest"})
c.subscribe(["mensagens"])
print(f"consumidor do grupo '{grupo}' aguardando... (Ctrl+C para sair)")
try:
    while True:
        m = c.poll(1.0)
        if m is None:
            continue
        if m.error():
            print("erro:", m.error())
            continue
        print(f"[{grupo}] particao {m.partition()} offset {m.offset()} chave={m.key().decode()} -> {m.value().decode()}")
except KeyboardInterrupt:
    pass
finally:
    c.close()
