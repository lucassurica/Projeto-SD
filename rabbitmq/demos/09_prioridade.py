"""Filas com prioridade (x-max-priority). Fila comum = FIFO; fila prioritária = maior prioridade primeiro.
Importante: a prioridade só reordena mensagens que estão ESPERANDO na fila (backlog)."""
from common import conectar, titulo

con = conectar(); ch = con.channel()
for f in ("fila_fifo", "fila_prioridade"):
    ch.queue_delete(f)
ch.queue_declare("fila_fifo")
ch.queue_declare("fila_prioridade", arguments={"x-max-priority": 10})

import pika
pedidos = [("limpar cache", 1), ("relatório mensal", 3), ("PAGAMENTO URGENTE", 9),
           ("enviar newsletter", 2), ("ALERTA DE FRAUDE", 10), ("backup", 1), ("emitir nota fiscal", 5)]

titulo("PRIORIDADE — 7 mensagens publicadas (sem consumidor ainda), prioridades misturadas")
for texto, prio in pedidos:
    ch.basic_publish("", "fila_fifo", texto.encode())
    ch.basic_publish("", "fila_prioridade", texto.encode(), properties=pika.BasicProperties(priority=prio))
    print(f"  publicada: prioridade={prio:<2} '{texto}'")

for fila in ("fila_fifo", "fila_prioridade"):
    print(f"\n  Consumindo '{fila}':")
    while True:
        m, props, corpo = ch.basic_get(fila, auto_ack=True)
        if m is None:
            break
        extra = f" (prioridade {props.priority})" if fila == "fila_prioridade" else ""
        print(f"    -> {corpo.decode()}{extra}")

for f in ("fila_fifo", "fila_prioridade"):
    ch.queue_delete(f)
con.close()
