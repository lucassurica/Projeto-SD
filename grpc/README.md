# gRPC - cliente envia mensagem ao servidor

    pip install -r requirements.txt
    python servidor.py      # terminal 1
    python cliente.py       # terminal 2 (voce digita no terminal)

O cliente mostra um menu com os 4 tipos de comunicacao do gRPC:
unario, streaming do servidor, streaming do cliente e bidirecional (chat).

Se precisar gerar o codigo a partir do contrato (ja vem gerado):

    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. mensagens.proto

Interoperabilidade: o mesmo `mensagens.proto` gera stubs para outras linguagens
(Java, Go, Node...), entao cliente e servidor podem estar em linguagens diferentes.
