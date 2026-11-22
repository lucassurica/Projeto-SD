"""Uso: python balanceamento_produtor.py [qtd]  -> envia qtd tarefas para a fila de trabalho"""
import sys
from comum import conectar

qtd = int(sys.argv[1]) if len(sys.argv) > 1 else 12
con = conectar()
ch = con.channel()
ch.queue_declare(queue="fila_trabalho", durable=True)
for i in range(1, qtd + 1):
    ch.basic_publish("", "fila_trabalho", f"tarefa {i}".encode())
print(f"{qtd} tarefas enviadas")
con.close()
