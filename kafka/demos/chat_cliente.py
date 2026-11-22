"""Cliente de mensagens Kafka: cada texto digitado é gravado no tópico 'mensagens'.
Não precisa do servidor no ar — o log do Kafka retém as mensagens."""
import sys

from common import *

nome = input("Seu nome: ").strip() or "anonimo"
esperar_broker()
garantir_topico("mensagens")
p = Producer({"bootstrap.servers": BOOT, "acks": "all", "log_level": 3})
print("Conectado ao Kafka. Digite mensagens (/sair ou Ctrl+D encerra).")


def confirmou(err, msg):
    if err:
        print(f"  ✘ erro: {err}", file=sys.stderr)
    else:
        print(f"  ✔ gravada em partição {msg.partition()}, offset {msg.offset()}")


while True:
    try:
        texto = input("> ").strip()
    except EOFError:
        break
    if texto == "/sair":
        break
    if not texto:
        continue
    p.produce("mensagens", key=nome, value=texto, callback=confirmou)
    p.flush()
