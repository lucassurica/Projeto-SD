"""Utilitários compartilhados pelas demos."""
import os
import time

import pika

HOST = os.getenv("RABBIT_HOST", "localhost")


def conectar(nome="demo"):
    for _ in range(60):
        try:
            return pika.BlockingConnection(pika.ConnectionParameters(
                HOST, heartbeat=30, client_properties={"connection_name": nome}))
        except pika.exceptions.AMQPConnectionError:
            time.sleep(1)
    raise RuntimeError("RabbitMQ indisponível")


def titulo(txt):
    print(f"\n{'=' * 72}\n{txt}\n{'=' * 72}", flush=True)


def limpar(ch, exchanges=(), filas=()):
    """Torna a demo repetível: apaga o que sobrou de execuções anteriores."""
    for f in filas:
        ch.queue_delete(f)
    for e in exchanges:
        ch.exchange_delete(e)


def esvaziar(ch, fila):
    """Lê tudo o que está na fila (basic_get) e devolve os corpos."""
    out = []
    while True:
        m, props, corpo = ch.basic_get(fila, auto_ack=True)
        if m is None:
            return out
        out.append(corpo.decode())


def mostrar_filas(ch, filas):
    """Mostra o que cada fila recebeu."""
    print("\nResultado — o que cada fila recebeu:")
    for f in filas:
        msgs = esvaziar(ch, f)
        print(f"  {f:<22} ({len(msgs)}): {msgs}")
