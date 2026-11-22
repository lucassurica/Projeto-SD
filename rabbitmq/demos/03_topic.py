"""TOPIC exchange: padrões com '*' (exatamente 1 palavra) e '#' (0 ou mais palavras)."""
from common import *

con = conectar(); ch = con.channel()
bindings = {
    "q_pedidos_criados": "pedido.*.criado",
    "q_todos_pedidos":   "pedido.#",
    "q_regiao_sp":       "*.sp.*",
    "q_cancelados":      "#.cancelado",
    "q_tudo":            "#",
}
limpar(ch, ["eventos_topic"], bindings)

titulo("TOPIC — roteamento por padrão (chave no formato palavra.palavra.palavra)")
ch.exchange_declare("eventos_topic", "topic")
for fila, padrao in bindings.items():
    ch.queue_declare(fila)
    ch.queue_bind(fila, "eventos_topic", routing_key=padrao)
    print(f"  binding: {fila:<18} <- padrão '{padrao}'")

print()
for chave in ["pedido.sp.criado", "pedido.rj.pago", "pedido.sp.cancelado", "estoque.sp.baixo"]:
    ch.basic_publish("eventos_topic", routing_key=chave, body=chave.encode())
    print(f"  publicado routing_key='{chave}'")

mostrar_filas(ch, bindings)
limpar(ch, ["eventos_topic"], bindings)
con.close()
