"""Uso: python persistencia.py enviar | ler
 Fila 'q_persistente': duravel + mensagens delivery_mode=2 (gravadas em disco)  -> sobrevive ao restart
 Fila 'q_transiente' : nao duravel + delivery_mode=1 (somente memoria)         -> perdida no restart
Roteiro: enviar -> docker compose restart rabbitmq -> ler
"""
import sys
import pika
from comum import conectar

con = conectar()
ch = con.channel()
ch.queue_declare(queue="q_persistente", durable=True)
ch.queue_declare(queue="q_transiente", durable=False)

if sys.argv[1] == "enviar":
    ch.basic_publish("", "q_persistente", b"msg PERSISTENTE",
                     pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))
    ch.basic_publish("", "q_transiente", b"msg TRANSIENTE",
                     pika.BasicProperties(delivery_mode=pika.DeliveryMode.Transient))
    print("enviada 1 mensagem para cada fila")
else:
    for fila in ("q_persistente", "q_transiente"):
        m, _, body = ch.basic_get(fila, auto_ack=True)
        print(f"{fila}: {body.decode() if m else '(vazia - mensagem perdida)'}")
con.close()
