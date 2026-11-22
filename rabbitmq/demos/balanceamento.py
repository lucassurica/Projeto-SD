"""Infra comum para as demos de balanceamento de carga entre consumidores."""
import threading
import time

from common import conectar


class Worker(threading.Thread):
    """Um 'processo' consumidor. peso = nº de consumers registrados na fila
    (é assim que se obtém round-robin PONDERADO no RabbitMQ)."""

    def __init__(self, nome, fila, peso=1, atraso=0.0, prefetch=0, registro=None, lock=None):
        super().__init__(daemon=True)
        self.nome, self.fila, self.peso, self.atraso, self.prefetch = nome, fila, peso, atraso, prefetch
        self.registro, self.lock = registro, lock
        self.pronto, self.parar, self.total = threading.Event(), threading.Event(), 0

    def run(self):
        con = conectar(f"worker-{self.nome}")
        ch = con.channel()
        ch.basic_qos(prefetch_count=self.prefetch)      # 0 = sem limite (round-robin puro)
        for _ in range(self.peso):
            ch.basic_consume(self.fila, self._cb)
        self.pronto.set()
        while not self.parar.is_set():
            con.process_data_events(time_limit=0.05)
        con.close()

    def _cb(self, ch, method, props, corpo):
        if self.atraso:
            time.sleep(self.atraso)                      # simula processamento
        self.total += 1
        with self.lock:
            self.registro.append(self.nome)
        ch.basic_ack(method.delivery_tag)


def rodar(fila, workers_cfg, n_msgs, titulo_txt):
    """Sobe os workers, publica n_msgs, espera terminarem e imprime a distribuição."""
    con = conectar("produtor"); ch = con.channel()
    ch.queue_delete(fila); ch.queue_declare(fila)
    registro, lock = [], threading.Lock()
    workers = [Worker(fila=fila, registro=registro, lock=lock, **cfg) for cfg in workers_cfg]
    for w in workers:
        w.start()
    for w in workers:
        w.pronto.wait()                                   # só publica depois que todos estão consumindo

    t0 = time.time()
    for i in range(1, n_msgs + 1):
        ch.basic_publish("", fila, f"tarefa {i}".encode())
    while len(registro) < n_msgs:
        time.sleep(0.05)
    dur = time.time() - t0
    for w in workers:
        w.parar.set()
    for w in workers:
        w.join()

    print(f"\n  {titulo_txt}")
    print(f"  ordem de conclusão: {' '.join(registro)}")
    for w in workers:
        barra = "█" * w.total
        print(f"  worker {w.nome} (peso={w.peso}, atraso={w.atraso}s, prefetch={w.prefetch}): {w.total:>2} msgs {barra}")
    print(f"  tempo total: {dur:.1f}s")
    ch.queue_delete(fila)
    con.close()
