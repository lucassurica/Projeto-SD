"""Produtor COM confirmacao (publisher confirms): o broker confirma que recebeu/gravou.
   'mandatory=True' devolve mensagens que nao puderam ser roteadas para nenhuma fila."""
import pika
from pika.exceptions import UnroutableError
from comum import conectar

con = conectar()
ch = con.channel()
ch.queue_declare(queue="fila_ack", durable=True)
ch.confirm_delivery()

for i in range(1, 6):
    try:
        ch.basic_publish("", "fila_ack", f"pedido {i}".encode(),
                         pika.BasicProperties(delivery_mode=2), mandatory=True)
        print(f"pedido {i}: broker CONFIRMOU")
    except UnroutableError:
        print(f"pedido {i}: devolvido (sem fila)")
try:
    ch.basic_publish("", "fila_que_nao_existe", b"x", mandatory=True)
except UnroutableError:
    print("fila inexistente: mensagem DEVOLVIDA ao produtor")
con.close()
