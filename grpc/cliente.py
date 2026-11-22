import time
import grpc
import mensagens_pb2 as pb
import mensagens_pb2_grpc as rpc


def main():
    with grpc.insecure_channel("localhost:50051") as canal:
        stub = rpc.MensageiroStub(canal)

        print("\n=== 1) Unario ===")
        r = stub.Enviar(pb.Mensagem(remetente="cliente", texto="Ola, servidor!"))
        print("resposta:", r.info)

        print("\n=== 2) Streaming do servidor ===")
        for m in stub.Inscrever(pb.Pedido(quantidade=3)):
            print("recebido:", m.texto)

        print("\n=== 3) Streaming do cliente ===")
        def gerar():
            for i in range(1, 4):
                yield pb.Mensagem(remetente="cliente", texto=f"parte {i}")
                time.sleep(0.3)
        print("resumo: total =", stub.EnviarVarias(gerar()).total)

        print("\n=== 4) Bidirecional ===")
        def conversa():
            for t in ["oi", "tudo bem?", "tchau"]:
                yield pb.Mensagem(remetente="cliente", texto=t)
                time.sleep(0.4)
        for m in stub.Chat(conversa()):
            print("recebido:", m.texto)


if __name__ == "__main__":
    main()
