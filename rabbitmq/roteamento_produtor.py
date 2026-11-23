"""Uso: python roteamento_produtor.py <direct|fanout|topic|headers>"""
import sys
import pika
from comum import conectar

tipo = sys.argv[1]
con = conectar()
ch = con.channel()
ch.exchange_declare(exchange=f"ex_{tipo}", exchange_type=tipo)

if tipo == "direct":
    for chave, txt in [("info", "log info"), ("erro", "log de erro"), ("aviso", "log de aviso")]:
        ch.basic_publish(f"ex_{tipo}", chave, txt.encode())
elif tipo == "fanout":
    for i in range(3):
        ch.basic_publish(f"ex_{tipo}", "", f"broadcast {i}".encode())
elif tipo == "topic":
    for chave in ["pagamento.erro", "pagamento.ok", "estoque.erro", "estoque.ok"]:
        ch.basic_publish(f"ex_{tipo}", chave, f"evento {chave}".encode())
elif tipo == "headers":
    for h in [{"formato": "pdf", "tipo": "relatorio"}, {"formato": "csv", "tipo": "relatorio"}]:
        ch.basic_publish(f"ex_{tipo}", "", f"doc {h}".encode(), pika.BasicProperties(headers=h))
print("mensagens enviadas")
con.close()
