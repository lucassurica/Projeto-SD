"""Cliente gRPC em Python."""
import os
import threading
import time

import grpc

import armazem_pb2 as pb
import armazem_pb2_grpc as pb_grpc

ALVO = os.getenv("GRPC_TARGET", "server:50051")
TOKEN = os.getenv("API_TOKEN", "segredo-sd")
META = (("authorization", f"Bearer {TOKEN}"),)


def titulo(txt):
    print(f"\n=== {txt} ===", flush=True)


def fmt(p):
    return f"#{p.id} {p.nome} [{pb.Categoria.Name(p.categoria)}] R$ {p.preco:.2f} (estoque {p.estoque})"


def main():
    print(f"[cliente] conectando em {ALVO}")
    canal = grpc.insecure_channel(ALVO)
    grpc.channel_ready_future(canal).result(timeout=15)
    stub = pb_grpc.ArmazemStub(canal)

    titulo("1) UNÁRIO — ConsultarProduto(1)")
    resp, call = stub.ConsultarProduto.with_call(pb.ProdutoRequest(id=1), metadata=META)
    print("resposta:", fmt(resp))
    print("metadata inicial do servidor:", dict(call.initial_metadata()))
    print("metadata final (trailers):  ", dict(call.trailing_metadata()))

    titulo("   Tratamento de erro — produto inexistente (NOT_FOUND)")
    try:
        stub.ConsultarProduto(pb.ProdutoRequest(id=999), metadata=META)
    except grpc.RpcError as e:
        print(f"erro capturado: {e.code().name} — {e.details()}")

    titulo("   Autenticação — sem token (UNAUTHENTICATED)")
    try:
        stub.ConsultarProduto(pb.ProdutoRequest(id=1))
    except grpc.RpcError as e:
        print(f"erro capturado: {e.code().name} — {e.details()}")

    titulo("2) SERVER STREAMING — ListarProdutos(categoria=ELETRONICOS)")
    t0 = time.time()
    for p in stub.ListarProdutos(pb.FiltroRequest(categoria=pb.ELETRONICOS), metadata=META):
        print(f"  +{time.time() - t0:.1f}s recebido: {fmt(p)}")

    titulo("3) CLIENT STREAMING — ImportarProdutos (envia 4, 1 inválido)")

    def gerar():
        itens = [
            pb.Produto(id=10, nome="Mouse", categoria=pb.ELETRONICOS, preco=80, estoque=30),
            pb.Produto(id=11, nome="Teclado", categoria=pb.ELETRONICOS, preco=150, estoque=20),
            pb.Produto(id=3, nome="Sistemas Distribuídos (2ª ed.)", categoria=pb.LIVROS, preco=130, estoque=5),
            pb.Produto(id=12, nome="", preco=-1),  # inválido
        ]
        for it in itens:
            print(f"  enviando: {it.id} {it.nome!r}")
            time.sleep(0.3)
            yield it

    r = stub.ImportarProdutos(gerar(), metadata=META)
    print(f"resumo: recebidos={r.recebidos} novos={r.novos} atualizados={r.atualizados} rejeitados={r.rejeitados}")

    titulo("4) BIDIRECIONAL — Negociar (Notebook custa 4500)")

    def ofertas():
        for v in (3000, 3800, 4100):
            print(f"  -> oferta {v}")
            yield pb.Oferta(produto_id=1, valor=v)
            time.sleep(0.6)

    for c in stub.Negociar(ofertas(), metadata=META):
        print(f"  <- aceita={c.aceita} valor={c.valor} \"{c.mensagem}\"")

    titulo("5) DEADLINE — OperacaoLenta(5s) com timeout de 1s")
    try:
        stub.OperacaoLenta(pb.LentaRequest(segundos=5), metadata=META, timeout=1)
    except grpc.RpcError as e:
        print(f"erro capturado: {e.code().name} — {e.details()}")

    print("\n[cliente] fim.")


if __name__ == "__main__":
    main()
