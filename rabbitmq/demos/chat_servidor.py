"""'Servidor' de mensagens RabbitMQ: consome a fila 'mensagens' e imprime o que chega."""
import time

from common import conectar

con = conectar("chat-servidor")
ch = con.channel()
ch.queue_declare("mensagens", durable=True)
ch.basic_qos(prefetch_count=1)


def ao_receber(ch, method, props, corpo):
    remetente = (props.headers or {}).get("remetente", "?")
    print(f"[{time.strftime('%H:%M:%S')}] de {remetente}: {corpo.decode()}", flush=True)
    ch.basic_ack(method.delivery_tag)          # confirma o processamento


ch.basic_consume("mensagens", ao_receber)
print("Servidor aguardando mensagens na fila 'mensagens' (Ctrl+C para sair)...", flush=True)
try:
    ch.start_consuming()
except KeyboardInterrupt:
    pass
