"""ROUND-ROBIN PONDERADO: o RabbitMQ distribui em round-robin entre CONSUMERS.
Se o worker A (máquina forte) registra 3 consumers e o B (fraca) registra 1,
a fila reparte 3:1 — o peso é o nº de consumers de cada worker."""
from common import titulo
from balanceamento import rodar

titulo("ROUND-ROBIN PONDERADO — pesos A=3, B=1 (proporção esperada 3:1)")
rodar("tarefas_ponderado",
      [dict(nome="A", peso=3), dict(nome="B", peso=1)],
      n_msgs=16, titulo_txt="16 mensagens, pesos 3:1 -> esperado A=12, B=4")

titulo("Outro exemplo — pesos A=1, B=2, C=3 (proporção 1:2:3)")
rodar("tarefas_ponderado2",
      [dict(nome="A", peso=1), dict(nome="B", peso=2), dict(nome="C", peso=3)],
      n_msgs=18, titulo_txt="18 mensagens -> esperado A=3, B=6, C=9")
