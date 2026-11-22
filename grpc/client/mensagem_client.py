"""Cliente de mensagens gRPC: digite um texto e ele é enviado ao servidor (chamada Enviar)."""
import os
import sys

import grpc

import armazem_pb2 as pb
import armazem_pb2_grpc as pb_grpc

ALVO = os.getenv("GRPC_TARGET", "server:50051")
META = (("authorization", f"Bearer {os.getenv('API_TOKEN', 'segredo-sd')}"),)

nome = input("Seu nome: ").strip() or "anonimo"
canal = grpc.insecure_channel(ALVO)
grpc.channel_ready_future(canal).result(timeout=15)
stub = pb_grpc.MensageiroStub(canal)
print(f"Conectado a {ALVO}. Digite mensagens (Ctrl+D ou /sair para encerrar).")

while True:
    try:
        texto = input("> ").strip()
    except EOFError:
        break
    if texto == "/sair":
        break
    if not texto:
        continue
    try:
        r = stub.Enviar(pb.Mensagem(remetente=nome, texto=texto), metadata=META, timeout=5)
        print(f"  ✔ servidor confirmou: mensagem #{r.numero} às {r.hora}")
    except grpc.RpcError as e:
        print(f"  ✘ erro: {e.code().name} — {e.details()}", file=sys.stderr)
