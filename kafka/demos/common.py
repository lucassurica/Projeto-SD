"""Utilitários compartilhados pelas demos de Kafka."""
import os
import time

from confluent_kafka import Consumer, KafkaException, Producer, TopicPartition  # noqa: F401
from confluent_kafka.admin import AdminClient, NewTopic

BOOT = os.getenv("KAFKA_BOOTSTRAP", "localhost:9094")


def titulo(txt):
    print(f"\n{'=' * 74}\n{txt}\n{'=' * 74}", flush=True)


def admin():
    return AdminClient({"bootstrap.servers": BOOT})


def esperar_broker():
    for _ in range(60):
        try:
            admin().list_topics(timeout=3)
            break
        except KafkaException:
            time.sleep(1)
    else:
        raise RuntimeError("Kafka indisponível")
    # Aquece o coordenador de grupos: na 1ª vez o broker cria o tópico interno __consumer_offsets,
    # o que leva alguns segundos e atrasaria o 1º consumer group.
    c = Consumer({"bootstrap.servers": BOOT, "group.id": "aquecimento"})
    for _ in range(40):
        try:
            c.committed([TopicPartition("__aquecimento", 0)], timeout=5)
            break
        except KafkaException:
            time.sleep(1)
    c.close()


def recriar_topico(nome, particoes=3, config=None):
    """Apaga (se existir) e cria o tópico, esperando o líder de cada partição ficar disponível."""
    a = admin()
    if nome in a.list_topics(timeout=10).topics:
        for f in a.delete_topics([nome]).values():
            f.result()
        for _ in range(100):
            if nome not in a.list_topics(timeout=10).topics:
                break
            time.sleep(0.2)
    for _ in range(40):
        try:
            for f in a.create_topics([NewTopic(nome, particoes, 1, config=config or {})]).values():
                f.result()
            break
        except Exception:
            time.sleep(0.5)
    for _ in range(100):
        t = a.list_topics(nome, timeout=5).topics.get(nome)
        if t and t.error is None and len(t.partitions) == particoes and all(p.leader >= 0 for p in t.partitions.values()):
            return
        time.sleep(0.2)


def produzir(topico, itens, **cfg):
    """itens: lista de (chave, valor). Devolve [(chave, partição, offset, valor)] na ordem de confirmação."""
    out = []

    def cb(err, msg):
        if err:
            raise KafkaException(err)
        out.append((msg.key().decode() if msg.key() else None, msg.partition(), msg.offset(), msg.value().decode()))

    p = Producer({"bootstrap.servers": BOOT, "acks": "all", "log_level": 3, **cfg})
    for k, v in itens:
        p.produce(topico, key=k, value=v, callback=cb)
        p.poll(0)
    p.flush()
    return out


def ler(grupo, topico, ociosidade=2.0, **cfg):
    """Consome até ficar `ociosidade` segundos sem mensagens; confirma (commit) os offsets ao final."""
    c = Consumer({"bootstrap.servers": BOOT, "group.id": grupo, "auto.offset.reset": "earliest",
                  "enable.auto.commit": False, **cfg})
    c.subscribe([topico])
    out, ultimo = [], time.time()
    while time.time() - ultimo < ociosidade:
        m = c.poll(0.3)
        if m is None or m.error():
            continue
        out.append((m.partition(), m.offset(), m.value().decode()))
        ultimo = time.time()
    if out:
        c.commit(asynchronous=False)
    c.close()
    return out
