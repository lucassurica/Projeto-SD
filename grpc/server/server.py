"""Servidor gRPC (Python) — demonstra os 4 tipos de RPC, metadata, auth por
interceptor, códigos de status e cancelamento/deadline."""
import os
import threading
import time
from concurrent import futures

import grpc

import armazem_pb2 as pb
import armazem_pb2_grpc as pb_grpc

TOKEN = os.getenv("API_TOKEN", "segredo-sd")
PORTA = os.getenv("PORT", "50051")

PRODUTOS = {
    1: pb.Produto(id=1, nome="Notebook", categoria=pb.ELETRONICOS, preco=4500.0, estoque=10, tags=["tech", "trabalho"]),
    2: pb.Produto(id=2, nome="Fone Bluetooth", categoria=pb.ELETRONICOS, preco=250.0, estoque=40, tags=["audio"]),
    3: pb.Produto(id=3, nome="Sistemas Distribuídos", categoria=pb.LIVROS, preco=120.0, estoque=15, tags=["faculdade"]),
    4: pb.Produto(id=4, nome="Clean Code", categoria=pb.LIVROS, preco=95.0, estoque=8, tags=["software"]),
    5: pb.Produto(id=5, nome="Café Especial 1kg", categoria=pb.ALIMENTOS, preco=65.0, estoque=100, tags=["bebida"]),
}
LOCK = threading.Lock()


def log(msg):
    print(f"[servidor] {msg}", flush=True)


# ----------------------------------------------------------------- Interceptor
class AuthInterceptor(grpc.ServerInterceptor):
    """Valida o header 'authorization' (metadata) antes de qualquer RPC.
    Equivale a um middleware: roda para os 4 tipos de chamada."""

    def intercept_service(self, continuation, details):
        handler = continuation(details)
        meta = dict(details.invocation_metadata)
        if handler is None or meta.get("authorization") == f"Bearer {TOKEN}":
            return handler

        log(f"{details.method} NEGADO (token ausente/inválido)")

        def negar(*_args):
            ctx = _args[-1]
            ctx.abort(grpc.StatusCode.UNAUTHENTICATED, "token inválido ou ausente")

        # O handler de substituição precisa ter o mesmo "formato" do original
        if handler.request_streaming and handler.response_streaming:
            return grpc.stream_stream_rpc_method_handler(negar)
        if handler.request_streaming:
            return grpc.stream_unary_rpc_method_handler(negar)
        if handler.response_streaming:
            return grpc.unary_stream_rpc_method_handler(negar)
        return grpc.unary_unary_rpc_method_handler(negar)


# --------------------------------------------------------------------- Serviço
class ArmazemServicer(pb_grpc.ArmazemServicer):
    # 1) UNÁRIO
    def ConsultarProduto(self, request, context):
        log(f"ConsultarProduto(id={request.id})")
        context.send_initial_metadata((("x-servidor", "armazem-python"),))
        produto = PRODUTOS.get(request.id)
        if produto is None:
            context.abort(grpc.StatusCode.NOT_FOUND, f"produto {request.id} não existe")
        context.set_trailing_metadata((("x-tempo-ms", "1"),))
        return produto

    # 2) SERVER STREAMING
    def ListarProdutos(self, request, context):
        log(f"ListarProdutos(categoria={pb.Categoria.Name(request.categoria)}, preco_max={request.preco_max})")
        for p in list(PRODUTOS.values()):
            if not context.is_active():          # cliente cancelou
                log("cliente cancelou o stream")
                return
            if request.categoria and p.categoria != request.categoria:
                continue
            if request.preco_max and p.preco > request.preco_max:
                continue
            time.sleep(0.4)                      # simula processamento: itens chegam aos poucos
            yield p

    # 3) CLIENT STREAMING
    def ImportarProdutos(self, request_iterator, context):
        resumo = pb.ResumoImportacao()
        for p in request_iterator:
            resumo.recebidos += 1
            if p.preco <= 0 or not p.nome:
                resumo.rejeitados += 1
                continue
            with LOCK:
                if p.id in PRODUTOS:
                    resumo.atualizados += 1
                else:
                    resumo.novos += 1
                PRODUTOS[p.id] = p
            log(f"  importado: {p.id} {p.nome}")
        log(f"ImportarProdutos -> {resumo.recebidos} recebidos")
        return resumo

    # 4) BIDIRECIONAL
    def Negociar(self, request_iterator, context):
        for oferta in request_iterator:
            produto = PRODUTOS.get(oferta.produto_id)
            if produto is None:
                yield pb.Contraoferta(aceita=False, valor=0, mensagem="produto inexistente")
                continue
            piso = produto.preco * 0.9
            if oferta.valor >= piso:
                yield pb.Contraoferta(aceita=True, valor=oferta.valor, mensagem="Fechado!")
            else:
                contra = round((oferta.valor + produto.preco) / 2, 2)
                yield pb.Contraoferta(aceita=False, valor=contra,
                                      mensagem=f"Muito baixo. Que tal {contra}?")

    # Deadline
    def OperacaoLenta(self, request, context):
        log(f"OperacaoLenta({request.segundos}s)")
        fim = time.time() + request.segundos
        while time.time() < fim:
            if not context.is_active():
                log("  deadline estourou/cliente cancelou — abortando trabalho no servidor")
                return pb.LentaReply()
            time.sleep(0.1)
        return pb.LentaReply(mensagem=f"terminei após {request.segundos}s")


def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                         interceptors=[AuthInterceptor()])
    pb_grpc.add_ArmazemServicer_to_server(ArmazemServicer(), server)
    server.add_insecure_port(f"[::]:{PORTA}")
    server.start()
    log(f"gRPC (Python) ouvindo na porta {PORTA}")
    server.wait_for_termination()


if __name__ == "__main__":
    main()
