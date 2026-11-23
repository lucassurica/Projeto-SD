"""Uso: python balanceamento_consumidor.py <nome> [--peso N] [--prefetch N] [--tempo SEG]
 Round-robin simples: todos com peso 1 (padrao).
 Round-robin PONDERADO: --peso 3 registra 3 consumidores da mesma fila neste processo;
   como o broker alterna entre consumidores, este processo recebe 3x mais mensagens.
 --prefetch N : ativa 'fair dispatch' (so recebe nova msg apos dar ack nas anteriores).
"""
import argparse, time
from comum import conectar

p = argparse.ArgumentParser()
p.add_argument("nome")
p.add_argument("--peso", type=int, default=1)
p.add_argument("--prefetch", type=int, default=0)
p.add_argument("--tempo", type=float, default=0.5)
a = p.parse_args()

con = conectar()
ch = con.channel()
ch.queue_declare(queue="fila_trabalho", durable=True)
if a.prefetch:
    ch.basic_qos(prefetch_count=a.prefetch)


def cb(ch, method, props, body):
    print(f"[{a.nome}] {body.decode()}")
    time.sleep(a.tempo)
    ch.basic_ack(method.delivery_tag)


for i in range(a.peso):
    ch.basic_consume(queue="fila_trabalho", on_message_callback=cb, consumer_tag=f"{a.nome}-{i}")
print(f"{a.nome} (peso {a.peso}) aguardando...")
ch.start_consuming()
