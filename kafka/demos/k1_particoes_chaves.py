"""Tópico = log particionado. A CHAVE da mensagem decide a partição (hash(chave) % nº partições).
Mesma chave -> mesma partição -> ORDEM preservada para aquela chave."""
from collections import defaultdict

from common import *

esperar_broker()
titulo("TÓPICO 'pedidos' com 3 PARTIÇÕES")
recriar_topico("pedidos", 3)
print("  criado: pedidos (partições=3, fator de replicação=1)")

clientes = ["cliente-A", "cliente-B", "cliente-C", "cliente-D"]
itens = [(clientes[i % 4], f"pedido {i // 4 + 1} de {clientes[i % 4]}") for i in range(12)]
print(f"\n  produzindo {len(itens)} mensagens com chave = cliente (acks=all)...")
res = produzir("pedidos", itens)

por_particao = defaultdict(list)
for chave, part, off, valor in res:
    por_particao[part].append((off, chave, valor))

print("\n  O LOG de cada partição (offset = posição imutável da mensagem na partição):")
for part in sorted(por_particao):
    print(f"\n  ── partição {part} ──")
    for off, chave, valor in sorted(por_particao[part]):
        print(f"     offset {off}: [{chave}] {valor}")

print("\n  => cada cliente caiu SEMPRE na mesma partição, e seus pedidos 1,2,3 estão em ordem.")
print("  => entre partições diferentes NÃO há garantia de ordem global (o preço da escalabilidade).")
