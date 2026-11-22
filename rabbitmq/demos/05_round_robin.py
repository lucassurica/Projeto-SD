"""Balanceamento de carga: ROUND-ROBIN (padrão do RabbitMQ) vs. despacho justo (prefetch=1)."""
from common import titulo
from balanceamento import rodar

titulo("ROUND-ROBIN — duas instâncias do mesmo serviço consumindo uma fila")
print("  A fila entrega 1 mensagem para cada consumidor, em sequência, sem olhar a carga.\n"
      "  Worker B é 10x mais lento — mesmo assim recebe a MESMA quantidade.")
rodar("tarefas_rr",
      [dict(nome="A(rapido)", atraso=0.02), dict(nome="B(lento)", atraso=0.2)],
      n_msgs=12, titulo_txt="Round-robin puro (prefetch ilimitado)")

titulo("DESPACHO JUSTO — basic_qos(prefetch_count=1)")
print("  O broker só entrega a próxima mensagem quando o consumidor deu ACK na anterior.\n"
      "  Quem é mais rápido naturalmente atende mais mensagens (balanceia por carga real).")
rodar("tarefas_justo",
      [dict(nome="A(rapido)", atraso=0.02, prefetch=1), dict(nome="B(lento)", atraso=0.2, prefetch=1)],
      n_msgs=12, titulo_txt="Despacho justo (prefetch=1)")
