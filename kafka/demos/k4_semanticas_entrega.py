"""Semânticas de entrega no consumidor, controladas pelo MOMENTO do commit do offset:
  at-least-once: processa e DEPOIS commita  -> crash = reprocessa (duplicata)
  at-most-once : commita e DEPOIS processa  -> crash = perde a mensagem
(exactly-once existe via produtor idempotente + transações; aqui mostramos o produtor idempotente.)"""
from common import *


def consumidor(grupo):
    c = Consumer({"bootstrap.servers": BOOT, "group.id": grupo, "auto.offset.reset": "earliest",
                  "enable.auto.commit": False})
    c.subscribe(["pagamentos"])
    return c


def proxima(c):
    for _ in range(60):
        m = c.poll(0.5)
        if m and not m.error():
            return m
    return None


def cenario(grupo, commit_antes):
    c = consumidor(grupo)
    for _ in range(4):                       # processa pagamentos 0..3; "cai" no 3
        m = proxima(c)
        n = m.value().decode()
        if commit_antes:
            c.commit(m, asynchronous=False)
            print(f"    commit offset {m.offset() + 1} -> processando {n} ...", end=" ")
        else:
            print(f"    processando {n} ...", end=" ")
        if m.offset() == 3:
            print("💥 CRASH!"); c.close(); break          # nunca chegou ao commit (at-least-once)
        print("ok")
        if not commit_antes:
            c.commit(m, asynchronous=False)
            print(f"    commit offset {m.offset() + 1}")
    print("    -- consumidor reinicia (mesmo grupo) --")
    c = consumidor(grupo)
    visto = []
    while (m := proxima(c)) is not None and len(visto) < 3:
        visto.append(m.value().decode()); c.commit(m, asynchronous=False)
        if m.offset() == 4:
            break
    c.close()
    print(f"    após reiniciar, leu: {visto}")


esperar_broker()
titulo("PRODUTOR IDEMPOTENTE + acks=all (sem duplicatas por retry do produtor)")
recriar_topico("pagamentos", 1)
res = produzir("pagamentos", [(None, f"pagamento-{i}") for i in range(5)], **{"enable.idempotence": True})
print(f"  5 pagamentos gravados (offsets {[r[2] for r in res]}) com enable.idempotence=true, acks=all")

titulo("AT-LEAST-ONCE: processa -> commit. Crash no pagamento-3 antes do commit")
cenario("grupo-at-least-once", commit_antes=False)
print("    => pagamento-3 foi LIDO DE NOVO: nada se perde, mas pode duplicar (torne o processamento idempotente).")

titulo("AT-MOST-ONCE: commit -> processa. Crash durante o pagamento-3")
cenario("grupo-at-most-once", commit_antes=True)
print("    => pagamento-3 NUNCA foi concluído e não será relido: pode PERDER, mas não duplica.")
