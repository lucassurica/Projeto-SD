"""'Servidor' de mensagens Kafka: consome o tópico 'mensagens' e imprime o que chega."""
import time

from common import *

esperar_broker()
garantir_topico("mensagens")
c = Consumer({"bootstrap.servers": BOOT, "group.id": "servidor-mensagens", "auto.offset.reset": "earliest"})
c.subscribe(["mensagens"])
print("Servidor aguardando mensagens no tópico 'mensagens' (Ctrl+C para sair)...", flush=True)
try:
    while True:
        m = c.poll(0.5)
        if m is None or m.error():
            continue
        remetente = m.key().decode() if m.key() else "?"
        print(f"[{time.strftime('%H:%M:%S')}] de {remetente}: {m.value().decode()}  (partição {m.partition()}, offset {m.offset()})", flush=True)
except KeyboardInterrupt:
    pass
finally:
    c.close()
