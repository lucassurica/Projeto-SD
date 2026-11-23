"""Uso: python roteamento_consumidor.py <direct|fanout|topic|headers> [chaves/padroes...]
  direct : chaves exatas        ex: python roteamento_consumidor.py direct erro
  fanout : ignora chave         ex: python roteamento_consumidor.py fanout
  topic  : padroes com * e #    ex: python roteamento_consumidor.py topic "*.erro" "pagamento.#"
  headers: pares k=v (todos)    ex: python roteamento_consumidor.py headers formato=pdf tipo=relatorio
"""
import sys
from comum import conectar

tipo = sys.argv[1]
args = sys.argv[2:]
con = conectar()
ch = con.channel()
ch.exchange_declare(exchange=f"ex_{tipo}", exchange_type=tipo)
fila = ch.queue_declare(queue="", exclusive=True).method.queue   # fila temporaria

if tipo == "fanout":
    ch.queue_bind(exchange=f"ex_{tipo}", queue=fila)
elif tipo == "headers":
    h = dict(a.split("=") for a in args)
    h["x-match"] = "all"      # troque por "any" para casar com qualquer header
    ch.queue_bind(exchange=f"ex_{tipo}", queue=fila, arguments=h)
else:
    for chave in args or [""]:
        ch.queue_bind(exchange=f"ex_{tipo}", queue=fila, routing_key=chave)


def cb(ch, method, props, body):
    print(f"[{tipo}] chave='{method.routing_key}' headers={props.headers} -> {body.decode()}")


ch.basic_consume(queue=fila, on_message_callback=cb, auto_ack=True)
print(f"Consumidor {tipo} aguardando... (Ctrl+C para sair)")
ch.start_consuming()
