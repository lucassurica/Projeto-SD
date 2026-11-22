"""Consumer group: as partições de um tópico são DIVIDIDAS entre os membros do grupo.
Mostra rebalanceamento ao entrar/sair consumidores e o limite (nº consumidores <= nº partições)."""
import threading
import time
from collections import defaultdict

from common import *

GRUPO = "faturamento"
encerrando = threading.Event()


class Membro(threading.Thread):
    def __init__(self, nome):
        super().__init__(daemon=True)
        self.nome, self.parts, self.recebidas = nome, [], defaultdict(int)
        self.parar = threading.Event()

    def run(self):
        c = Consumer({"bootstrap.servers": BOOT, "group.id": GRUPO, "client.id": self.nome,
                      "auto.offset.reset": "latest", "session.timeout.ms": 6000, "heartbeat.interval.ms": 1000})

        def atribuiu(_, ps):
            self.parts = sorted(p.partition for p in ps)
            if not encerrando.is_set():
                print(f"      [{self.nome}] recebeu partições {self.parts}", flush=True)

        def revogou(_, ps):
            self.parts = []

        c.subscribe(["pedidos-grupo"], on_assign=atribuiu, on_revoke=revogou)
        while not self.parar.is_set():
            m = c.poll(0.2)
            if m and not m.error():
                self.recebidas[m.partition()] += 1
        c.close()                              # sai do grupo "educadamente" -> rebalanceamento imediato


def estagio(txt, membros, espera=8):
    print(f"\n  ▶ {txt}")
    for m in membros:
        m.recebidas.clear()
    time.sleep(espera)
    print("    situação (msgs recebidas neste estágio):")
    for m in membros:
        total = sum(m.recebidas.values())
        print(f"      {m.nome}: partições={m.parts or '— (ocioso)'}  msgs={total} {'█' * (total // 3)}")


esperar_broker()
titulo("CONSUMER GROUP 'faturamento' — 3 partições, consumidores entrando e saindo")
recriar_topico("pedidos-grupo", 3)

parar_prod = threading.Event()


def produtor_continuo():
    p = Producer({"bootstrap.servers": BOOT})
    i = 0
    while not parar_prod.is_set():
        p.produce("pedidos-grupo", key=f"cliente-{i % 9}", value=f"pedido {i}")
        p.poll(0); i += 1
        time.sleep(0.1)
    p.flush()


threading.Thread(target=produtor_continuo, daemon=True).start()
print("  (um produtor envia ~10 pedidos/s para o tópico durante toda a demo)")

c1, c2, c3, c4 = (Membro(f"consumidor-{i}") for i in range(1, 5))
c1.start(); estagio("consumidor-1 entra no grupo -> fica com TODAS as partições", [c1])
c2.start(); estagio("consumidor-2 entra -> REBALANCEAMENTO: partições divididas", [c1, c2])
c3.start(); estagio("consumidor-3 entra -> 1 partição para cada", [c1, c2, c3])
c4.start(); estagio("consumidor-4 entra -> mais consumidores que partições: um fica OCIOSO", [c1, c2, c3, c4])
c1.parar.set(); c1.join()
estagio("consumidor-1 sai (ou cai) -> rebalanceamento: o ocioso assume", [c2, c3, c4])

parar_prod.set(); encerrando.set()
for m in (c2, c3, c4):
    m.parar.set(); m.join()
print("\n  => escalar consumo = adicionar consumidores ao grupo (até o nº de partições).")
