import time
from concurrent import futures
import grpc
import mensagens_pb2 as pb
import mensagens_pb2_grpc as rpc


class Mensageiro(rpc.MensageiroServicer):
    # 1) Unario: 1 requisicao -> 1 resposta
    def Enviar(self, request, context):
        print(f"[unario] {request.remetente}: {request.texto}")
        return pb.Confirmacao(recebida=True, info=f"Servidor recebeu: {request.texto}")

    # 2) Streaming do servidor: 1 requisicao -> N respostas
    def Inscrever(self, request, context):
        for i in range(1, request.quantidade + 1):
            print(f"[server-stream] enviando {i}/{request.quantidade}")
            yield pb.Mensagem(remetente="servidor", texto=f"Notificacao {i}")
            time.sleep(0.5)

    # 3) Streaming do cliente: N requisicoes -> 1 resposta
    def EnviarVarias(self, request_iterator, context):
        total = 0
        for msg in request_iterator:
            total += 1
            print(f"[client-stream] {msg.remetente}: {msg.texto}")
        return pb.Resumo(total=total)

    # 4) Bidirecional: N requisicoes <-> N respostas (independentes)
    def Chat(self, request_iterator, context):
        for msg in request_iterator:
            print(f"[chat] {msg.remetente}: {msg.texto}")
            yield pb.Mensagem(remetente="servidor", texto=f"eco: {msg.texto}")


def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    rpc.add_MensageiroServicer_to_server(Mensageiro(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Servidor gRPC em :50051", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    main()
