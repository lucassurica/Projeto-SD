"""DIRECT exchange: roteia quando routing_key == binding_key (casamento exato)."""
from common import *

con = conectar(); ch = con.channel()
filas = ["q_erros", "q_avisos_infos", "q_tudo"]
limpar(ch, ["logs_direct"], filas)

titulo("DIRECT — roteamento por chave exata")
ch.exchange_declare("logs_direct", "direct")
bindings = {"q_erros": ["error"], "q_avisos_infos": ["warning", "info"], "q_tudo": ["error", "warning", "info"]}
for fila, chaves in bindings.items():
    ch.queue_declare(fila)
    for k in chaves:
        ch.queue_bind(fila, "logs_direct", routing_key=k)
    print(f"  binding: {fila:<16} <- chaves {chaves}")

print()
for sev in ["info", "warning", "error", "debug"]:
    ch.basic_publish("logs_direct", routing_key=sev, body=f"[{sev}] msg".encode())
    print(f"  publicado routing_key='{sev}'")
print("  (note: 'debug' não tem binding algum -> a mensagem é descartada pela exchange)")

mostrar_filas(ch, filas)

titulo("Bônus: exchange PADRÃO ('') — direct implícito: routing_key = nome da fila")
ch.queue_declare("fila_direta")
ch.basic_publish("", routing_key="fila_direta", body=b"entrega direta na fila pelo nome")
mostrar_filas(ch, ["fila_direta"])
limpar(ch, ["logs_direct"], filas + ["fila_direta"])
con.close()
