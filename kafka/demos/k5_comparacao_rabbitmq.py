"""Mesmo cenário nos dois brokers: 5 mensagens, um consumidor as lê e dá ack/commit.
Depois chega um NOVO consumidor/grupo. O que ele encontra?"""
import pika

from common import *
import os

esperar_broker()
N = 5

# ----------------------------------------------------------------- RabbitMQ
titulo("RabbitMQ — modelo de FILA (a mensagem é removida ao ser confirmada)")
con = None
for _ in range(60):
    try:
        con = pika.BlockingConnection(pika.ConnectionParameters(os.getenv("RABBIT_HOST", "rabbitmq")))
        break
    except Exception:
        time.sleep(1)
ch = con.channel()
ch.queue_delete("cmp"); ch.queue_declare("cmp", durable=True)
for i in range(N):
    ch.basic_publish("", "cmp", f"msg-{i}".encode())
lidas = []
while True:
    m, _, corpo = ch.basic_get("cmp")
    if m is None:
        break
    lidas.append(corpo.decode()); ch.basic_ack(m.delivery_tag)
print(f"  consumidor A leu e deu ack: {lidas}")
m, _, corpo = ch.basic_get("cmp")
print(f"  consumidor B (novo) tenta ler: {'nada — fila vazia, mensagens foram REMOVIDAS' if m is None else corpo}")
print(f"  mensagens ainda disponíveis: {ch.queue_declare('cmp', passive=True).method.message_count}")
ch.queue_delete("cmp"); con.close()

# ------------------------------------------------------------------- Kafka
titulo("Kafka — modelo de LOG (a mensagem permanece; cada grupo tem seu offset)")
recriar_topico("cmp", 1)
produzir("cmp", [(None, f"msg-{i}") for i in range(N)])
a = ler("grupo-A", "cmp")
print(f"  grupo A leu e commitou: {[m[2] for m in a]}")
b = ler("grupo-B", "cmp")
print(f"  grupo B (novo) lê desde o início: {[m[2] for m in b]}  -> as mensagens CONTINUAM lá")
a2 = ler("grupo-A", "cmp")
print(f"  grupo A de novo: {len(a2)} msgs (seu offset já avançou)")

titulo("RESUMO — RabbitMQ x Kafka")
print("""
  Aspecto             RabbitMQ                              Kafka
  ------------------  ------------------------------------  ------------------------------------
  Modelo              Fila / broker "inteligente"           Log distribuído / broker "simples"
  Após consumir       Mensagem REMOVIDA (ack)               Mensagem RETIDA (tempo/tamanho)
  Releitura (replay)  Não                                   Sim (seek por offset)
  Quem controla       Broker empurra (push) ao consumidor   Consumidor puxa (pull) e guarda offset
  Roteamento          Exchanges: direct/fanout/topic/hdrs   Só tópico + partição (chave)
  Ordem               Por fila (c/ 1 consumidor)            Por partição
  Escala consumo      Competing consumers na fila           Consumer group <= nº de partições
  Prioridade/TTL/DLQ  Nativos                               Não nativos
  Throughput          Dezenas de milhares msg/s             Centenas de milhares a milhões msg/s
  Caso típico         Tarefas, RPC, workflows, roteamento   Streaming, event sourcing, logs, ETL
""")
