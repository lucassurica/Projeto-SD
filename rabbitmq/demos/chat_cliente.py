"""Cliente de mensagens RabbitMQ: cada texto digitado é publicado na fila 'mensagens'.
Note: o cliente NÃO precisa do servidor no ar — o broker guarda as mensagens até alguém consumir."""
import sys

import pika

from common import conectar

nome = input("Seu nome: ").strip() or "anonimo"
con = conectar("chat-cliente")
ch = con.channel()
ch.queue_declare("mensagens", durable=True)
ch.confirm_delivery()                           # broker confirma cada publicação
print("Conectado ao RabbitMQ. Digite mensagens (/sair ou Ctrl+D encerra).")

while True:
    try:
        texto = input("> ").strip()
    except EOFError:
        break
    if texto == "/sair":
        break
    if not texto:
        continue
    try:
        ch.basic_publish("", "mensagens", texto.encode(), mandatory=True,
                         properties=pika.BasicProperties(delivery_mode=2, headers={"remetente": nome}))
        print("  ✔ broker confirmou o recebimento")
    except Exception as e:
        print(f"  ✘ erro: {e}", file=sys.stderr)
con.close()
