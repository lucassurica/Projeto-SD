import pika


def conectar():
    return pika.BlockingConnection(pika.ConnectionParameters("localhost"))
