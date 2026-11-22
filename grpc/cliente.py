"""Cliente gRPC interativo: voce digita no terminal e o servidor responde."""
import queue
import threading
import grpc
import mensagens_pb2 as pb
import mensagens_pb2_grpc as rpc

NOME = input("Seu nome: ").strip() or "cliente"

MENU = """
=== Menu gRPC ===
1) Enviar uma mensagem            (unario)
2) Receber N notificacoes         (streaming do servidor)
3) Enviar varias mensagens        (streaming do cliente)
4) Chat com o servidor            (bidirecional)
0) Sair
"""


def unario(stub):
    texto = input("Mensagem: ")
    r = stub.Enviar(pb.Mensagem(remetente=NOME, texto=texto))
    print("Servidor respondeu:", r.info)


def stream_servidor(stub):
    n = int(input("Quantas notificacoes? "))
    for m in stub.Inscrever(pb.Pedido(quantidade=n)):
        print("Recebido:", m.texto)


def stream_cliente(stub):
    print("Digite as mensagens (linha vazia para terminar):")

    def gerar():
        while True:
            linha = input("> ")
            if not linha:
                return
            yield pb.Mensagem(remetente=NOME, texto=linha)

    print("Servidor recebeu", stub.EnviarVarias(gerar()).total, "mensagens")


def chat(stub):
    print("Chat iniciado. Digite '/sair' para encerrar.")
    saida = queue.Queue()
    FIM = object()

    def gerar():
        while True:
            item = saida.get()
            if item is FIM:
                return
            yield pb.Mensagem(remetente=NOME, texto=item)

    respostas = stub.Chat(gerar())

    def ouvir():
        for m in respostas:
            print(f"\n[{m.remetente}] {m.texto}")

    t = threading.Thread(target=ouvir)
    t.start()
    while True:
        linha = input("voce> ")
        if linha.strip() == "/sair":
            saida.put(FIM)
            break
        saida.put(linha)
    t.join()


def main():
    with grpc.insecure_channel("localhost:50051") as canal:
        stub = rpc.MensageiroStub(canal)
        acoes = {"1": unario, "2": stream_servidor, "3": stream_cliente, "4": chat}
        while True:
            print(MENU)
            op = input("Escolha: ").strip()
            if op == "0":
                break
            if op in acoes:
                try:
                    acoes[op](stub)
                except grpc.RpcError as e:
                    print("Erro de comunicacao:", e.code())
            else:
                print("Opcao invalida")


if __name__ == "__main__":
    main()
