"""FANOUT exchange: copia a mensagem para TODAS as filas ligadas (ignora routing_key). Pub/Sub."""
from common import *

con = conectar(); ch = con.channel()
filas = ["q_email", "q_sms", "q_auditoria"]
limpar(ch, ["eventos_fanout"], filas)

titulo("FANOUT — broadcast / publish-subscribe")
ch.exchange_declare("eventos_fanout", "fanout")
for f in filas:
    ch.queue_declare(f)
    ch.queue_bind(f, "eventos_fanout")           # sem routing key
    print(f"  binding: {f} <- eventos_fanout")

print()
for i in (1, 2):
    ch.basic_publish("eventos_fanout", routing_key="qualquer-coisa-e-ignorada", body=f"pedido #{i} criado".encode())
    print(f"  publicada 1 mensagem: 'pedido #{i} criado'")

mostrar_filas(ch, filas)
print("\n  => 1 publicação virou 1 cópia em CADA fila (3 assinantes independentes).")
limpar(ch, ["eventos_fanout"], filas)
con.close()
