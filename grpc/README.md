# gRPC - cliente envia mensagem ao servidor

    pip install -r requirements.txt
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. mensagens.proto   # (ja incluso gerado)
    python servidor.py      # terminal 1
    python cliente.py       # terminal 2

Mostra os 4 tipos de comunicacao: unario, streaming do servidor, do cliente e bidirecional.
Interoperabilidade: o mesmo `mensagens.proto` gera stubs para outras linguagens
(ex.: Java, Go, Node), entao o cliente pode estar em Node e o servidor em Python.
