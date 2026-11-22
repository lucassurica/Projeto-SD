"""Com e sem confirmação de recebimento:
  A) consumidor com AUTO-ACK  que 'cai'  -> mensagem PERDIDA
  B) consumidor com ACK MANUAL que 'cai' -> mensagem REENTREGUE (redelivered)
  C) nack(requeue=False) -> Dead Letter Queue
  D) lado do PRODUTOR: publisher confirms + mandatory (mensagem não roteável)"""
import time

import pika
from pika.exceptions import UnroutableError

from common import conectar, titulo

con = conectar(); ch = con.channel()
for f in ("conf_auto", "conf_manual", "conf_trabalho", "conf_mortas"):
    ch.queue_delete(f)
ch.exchange_delete("conf_dlx")

# ------------------------------------------------------------------ A
titulo("A) SEM confirmação (auto_ack=True) — consumidor cai com a mensagem em mãos")
ch.queue_declare("conf_auto")
ch.basic_publish("", "conf_auto", b"pagamento #1")
c1 = conectar("consumidor-1"); ch1 = c1.channel()
m, _, corpo = ch1.basic_get("conf_auto", auto_ack=True)         # broker JÁ descarta ao entregar
print(f"  consumidor-1 recebeu '{corpo.decode()}' (auto-ack: broker considera entregue)")
c1.close(); print("  consumidor-1 CAIU antes de processar!")
print(f"  mensagens restantes na fila: {ch.queue_declare('conf_auto', passive=True).method.message_count}"
      "  -> MENSAGEM PERDIDA")

# ------------------------------------------------------------------ B
titulo("B) COM confirmação manual (basic_ack) — mesmo cenário")
ch.queue_declare("conf_manual")
ch.basic_publish("", "conf_manual", b"pagamento #2")
c1 = conectar("consumidor-1"); ch1 = c1.channel()
m, _, corpo = ch1.basic_get("conf_manual", auto_ack=False)
print(f"  consumidor-1 recebeu '{corpo.decode()}' mas ainda NÃO deu ack (unacked)")
print(f"  (unacked no broker: mensagem em trânsito, não está 'ready' na fila)")
c1.close(); print("  consumidor-1 CAIU antes do ack!")
c2 = conectar("consumidor-2"); ch2 = c2.channel()
m, _, corpo = ch2.basic_get("conf_manual", auto_ack=False)
print(f"  consumidor-2 recebeu '{corpo.decode()}' redelivered={m.redelivered}  -> REENTREGUE, nada perdido")
ch2.basic_ack(m.delivery_tag); print("  consumidor-2 deu ack: agora sim o broker remove a mensagem")
c2.close()

# ------------------------------------------------------------------ C
titulo("C) Rejeição (nack, requeue=False) + Dead Letter Exchange")
ch.exchange_declare("conf_dlx", "direct")
ch.queue_declare("conf_mortas"); ch.queue_bind("conf_mortas", "conf_dlx", "mortas")
ch.queue_declare("conf_trabalho", arguments={"x-dead-letter-exchange": "conf_dlx",
                                             "x-dead-letter-routing-key": "mortas"})
ch.basic_publish("", "conf_trabalho", b"mensagem-venenosa")
m, _, corpo = ch.basic_get("conf_trabalho")
print(f"  consumidor recebeu '{corpo.decode()}' e não consegue processar -> basic_nack(requeue=False)")
ch.basic_nack(m.delivery_tag, requeue=False)
for _ in range(40):                       # o dead-lettering é assíncrono: espera chegar
    m, props, corpo = ch.basic_get("conf_mortas", auto_ack=True)
    if m:
        break
    time.sleep(0.1)
morte = props.headers["x-death"][0]
print(f"  chegou na DLQ: '{corpo.decode()}' (motivo={morte['reason']}, fila de origem={morte['queue']})")

# ------------------------------------------------------------------ D
titulo("D) Confirmação do PRODUTOR — publisher confirms + mandatory")
ch.confirm_delivery()
ch.basic_publish("", "conf_trabalho", b"ok", mandatory=True)
print("  publicar na fila existente -> broker CONFIRMOU (ack do publisher confirm)")
try:
    ch.basic_publish("", "fila-que-nao-existe", b"ok", mandatory=True)
except UnroutableError:
    print("  publicar em fila inexistente com mandatory=True -> broker DEVOLVEU (basic.return): produtor fica sabendo")

for f in ("conf_auto", "conf_manual", "conf_trabalho", "conf_mortas"):
    ch.queue_delete(f)
ch.exchange_delete("conf_dlx")
con.close()
