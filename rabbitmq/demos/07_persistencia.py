"""Persistente x transiente (com confirmação do broker — publisher confirms).
Uso: 07_persistencia.py publicar   -> publica e mostra os confirms
     (reiniciar o broker)
     07_persistencia.py verificar  -> mostra o que sobreviveu"""
import sys

import pika
from pika.exceptions import ChannelClosedByBroker

from common import conectar, titulo

CASOS = [
    # (fila, durável?, delivery_mode, descrição)
    ("fila_duravel__msg_persistente", True, 2, "fila durável + msg PERSISTENTE"),
    ("fila_duravel__msg_transiente",  True, 1, "fila durável + msg TRANSIENTE"),
    ("fila_transiente__msg_persist",  False, 2, "fila NÃO durável + msg persistente"),
]

if sys.argv[1:] == ["publicar"]:
    con = conectar(); ch = con.channel()
    ch.confirm_delivery()                    # PUBLISHER CONFIRMS: broker confirma (ack) cada publicação
    titulo("PUBLICANDO 3 mensagens em cada fila (com publisher confirms)")
    for fila, duravel, modo, desc in CASOS:
        ch.queue_delete(fila)
        ch.queue_declare(fila, durable=duravel)
        for i in range(3):
            ch.basic_publish("", fila, f"msg{i}".encode(),
                             properties=pika.BasicProperties(delivery_mode=modo), mandatory=True)
        print(f"  {desc:<40} -> 3 msgs publicadas e CONFIRMADAS pelo broker")
    print("\n  Agora: reinicie o broker (docker compose restart rabbitmq) e rode 'verificar'.")
    con.close()

elif sys.argv[1:] == ["verificar"]:
    con = conectar()
    titulo("APÓS O RESTART DO BROKER — o que sobreviveu?")
    for fila, duravel, modo, desc in CASOS:
        ch = con.channel()
        try:
            n = ch.queue_declare(fila, passive=True).method.message_count
            print(f"  {desc:<40} -> fila existe, {n} mensagem(ns)")
        except ChannelClosedByBroker:
            print(f"  {desc:<40} -> fila NÃO EXISTE mais (perdida)")
    con.close()
    print("\n  Só sobrevive: fila DURÁVEL + mensagem PERSISTENTE (delivery_mode=2).")
else:
    sys.exit("uso: 07_persistencia.py publicar|verificar")
