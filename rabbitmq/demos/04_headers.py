"""HEADERS exchange: roteia pelos cabeçalhos da mensagem (não pela routing_key).
x-match=all -> todos os headers devem casar; x-match=any -> basta um."""
from common import *

con = conectar(); ch = con.channel()
filas = {
    "q_pdf_urgente": {"x-match": "all", "formato": "pdf", "prioridade": "alta"},
    "q_pdf_ou_web":  {"x-match": "any", "formato": "pdf", "origem": "web"},
    "q_png":         {"x-match": "all", "formato": "png"},
}
limpar(ch, ["docs_headers"], filas)

titulo("HEADERS — roteamento por atributos")
ch.exchange_declare("docs_headers", "headers")
for fila, args in filas.items():
    ch.queue_declare(fila)
    ch.queue_bind(fila, "docs_headers", arguments=args)
    print(f"  binding: {fila:<14} <- {args}")

print()
msgs = {
    "doc1": {"formato": "pdf", "prioridade": "alta"},
    "doc2": {"formato": "pdf", "prioridade": "baixa"},
    "doc3": {"formato": "png", "origem": "web"},
    "doc4": {"formato": "txt", "origem": "mobile"},
}
for nome, hdr in msgs.items():
    ch.basic_publish("docs_headers", routing_key="",
                     properties=pika.BasicProperties(headers=hdr), body=nome.encode())
    print(f"  publicado {nome} com headers {hdr}")

mostrar_filas(ch, filas)
limpar(ch, ["docs_headers"], filas)
con.close()
