"""Uso: python confirmacao_consumidor.py <auto|manual> [--falhar]
 auto  : auto_ack=True  -> broker considera entregue ao enviar; se o consumidor cair, a msg SE PERDE.
 manual: basic_ack apos processar; se o consumidor cair sem ack, a msg volta para a fila e e REENTREGUE.
 --falhar: o consumidor 'cai' ao receber o pedido 3 (antes de processar/confirmar)."""
import os, sys
from comum import conectar

modo = sys.argv[1]
falhar = "--falhar" in sys.argv
con = conectar()
ch = con.channel()
ch.queue_declare(queue="fila_ack", durable=True)


def cb(ch, method, props, body):
    txt = body.decode()
    print(f"recebido: {txt} (redelivered={method.redelivered})", flush=True)
    if falhar and txt == "pedido 3":
        print(">>> consumidor caiu sem confirmar!", flush=True)
        os._exit(1)
    if modo == "manual":
        ch.basic_ack(method.delivery_tag)
        print(f"   ack enviado para {txt}")


ch.basic_consume(queue="fila_ack", on_message_callback=cb, auto_ack=(modo == "auto"))
print(f"modo {modo} aguardando...")
ch.start_consuming()
