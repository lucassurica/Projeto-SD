"""Uso: python prioridade.py enviar | ler
 Envia mensagens em ordem de prioridade embaralhada SEM consumidor; ao ler, as de
 maior prioridade saem primeiro. A fila precisa de x-max-priority na declaracao."""
import random, sys
import pika
from comum import conectar

con = conectar()
ch = con.channel()
ch.queue_declare(queue="fila_prioridade", durable=True, arguments={"x-max-priority": 10})

if sys.argv[1] == "enviar":
    prios = list(range(0, 10))
    random.shuffle(prios)
    for p in prios:
        ch.basic_publish("", "fila_prioridade", f"mensagem prioridade {p}".encode(),
                         pika.BasicProperties(priority=p))
        print(f"enviada: prioridade {p}")
else:
    while True:
        m, props, body = ch.basic_get("fila_prioridade", auto_ack=True)
        if not m:
            break
        print("lida:", body.decode())
con.close()
