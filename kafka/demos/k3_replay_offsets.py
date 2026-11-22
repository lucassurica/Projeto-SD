"""O Kafka NÃO apaga a mensagem quando ela é consumida: é um LOG retido por tempo/tamanho.
Cada GRUPO tem seu próprio offset -> vários grupos leem tudo, de forma independente, e é possível reler (replay)."""
from common import *

esperar_broker()
titulo("LOG RETIDO — produzindo 10 eventos no tópico 'eventos'")
recriar_topico("eventos", 2)
produzir("eventos", [(f"k{i}", f"evento-{i}") for i in range(10)])
print("  10 eventos gravados.")


def mostrar(rotulo, msgs):
    print(f"  {rotulo}: {len(msgs)} msgs " + (f"-> {[m[2] for m in sorted(msgs)]}" if msgs else ""))


titulo("1) Grupo 'relatorios' lê tudo e confirma (commit) os offsets")
mostrar("relatorios", ler("relatorios", "eventos"))

titulo("2) Mesmo grupo 'relatorios' de novo — offsets já confirmados, nada novo")
mostrar("relatorios", ler("relatorios", "eventos"))

titulo("3) Grupo DIFERENTE 'antifraude' — recebe TODAS as 10 (as mensagens não sumiram)")
mostrar("antifraude", ler("antifraude", "eventos"))

titulo("4) REPLAY — reler a partir de um offset escolhido (partição 0, offset 2)")
c = Consumer({"bootstrap.servers": BOOT, "group.id": "replay-manual", "enable.auto.commit": False})
c.assign([TopicPartition("eventos", 0, 2)])
lidas, ocioso = [], time.time()
while time.time() - ocioso < 2:
    m = c.poll(0.3)
    if m and not m.error():
        lidas.append((m.partition(), m.offset(), m.value().decode())); ocioso = time.time()
c.close()
for p, o, v in lidas:
    print(f"    partição {p} offset {o}: {v}")
print("  => o consumidor controla a posição de leitura (seek). Útil p/ reprocessar após um bug.")

titulo("5) Retenção do tópico (quanto tempo o log fica guardado)")
from confluent_kafka.admin import ConfigResource
a = admin()
cr = ConfigResource(ConfigResource.Type.TOPIC, "eventos")
cfg = list(a.describe_configs([cr]).values())[0].result()
for chave in ("retention.ms", "retention.bytes", "cleanup.policy"):
    print(f"    {chave} = {cfg[chave].value}")
print("    (retention.ms=604800000 -> 7 dias, independente de a mensagem ter sido lida)")
