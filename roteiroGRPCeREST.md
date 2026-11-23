Vídeo gRPC (~4 min)
0:00 a 0:15, abertura

[TELA] Terminal vazio.

"Olá! Neste vídeo vou demonstrar o gRPC, um framework de chamada de procedimento remoto."

0:15 a 1:30, teoria

[TELA] Slide 16 (as etapas do RPC) ou um desenho de cliente, stub, rede, stub e servidor.

"Na aula, vimos que o RPC permite a um processo chamar um procedimento em outra máquina como se fosse local. Nenhum aspecto da troca de mensagens fica visível para o programador. Essa transparência vem dos stubs: o stub do cliente empacota os parâmetros em uma mensagem e a envia, e o stub do servidor desempacota, executa o procedimento e devolve o resultado.

Para cliente e servidor concordarem no formato das mensagens, a interface é descrita em uma IDL, que é compilada e gera os dois stubs. No gRPC, a IDL é o arquivo .proto.

Nos eixos da aula, o gRPC é transiente, porque os dois lados precisam estar rodando. Ele roda sobre HTTP/2 e TCP, então é confiável. A chamada unária é síncrona: o cliente fica bloqueado até a resposta. E ele suporta tanto mensagens discretas quanto fluxo, nos modos de streaming."

1:30 a 2:15, contrato e stubs

[TELA] Abra o mensagens.proto, depois rode o protoc e abra o mensagens_pb2_grpc.py.

"Este é o contrato: um serviço com quatro métodos. Rodando o compilador, ele gera o código de rede. Este mensagens_pb2_grpc.py é o stub: o cliente o usa para chamar o servidor como uma função local, sem escrever código de socket. E o mesmo .proto poderia gerar o stub em Java, Node ou Go, então cliente e servidor podem estar em linguagens diferentes."

2:15 a 3:45, demo

[TELA] Servidor à esquerda, cliente à direita.

"Subo o servidor e o cliente interativo. Escolho a opção 1, unário: digito uma mensagem e o servidor responde. O cliente esperou a resposta, então é síncrono.

Opção 2, streaming do servidor: peço 3 notificações e elas chegam uma a uma, a partir de uma única requisição.

Opção 3, streaming do cliente: envio várias mensagens e o servidor responde só no fim, com o total.

Opção 4, o chat bidirecional: os dois lados trocam mensagens ao mesmo tempo, de forma independente. Digito duas e saio com /sair."

[TELA] Pare o servidor (Ctrl+C), volte ao cliente e escolha a opção 1.

"Por fim, o caráter transiente. Se eu derrubo o servidor e envio uma mensagem, a chamada falha com o erro unavailable. Ninguém guardou a mensagem: diferente do RabbitMQ, aqui o receptor precisa estar ativo."

3:45 a 4:10, fechamento

"Em resumo: contrato forte na IDL, quatro modos de comunicação e interoperabilidade entre linguagens. Como o professor comentou, frameworks de RPC como o gRPC disputam hoje espaço com o REST. Obrigado!"

Vídeo REST (~3 min 30 s)
0:00 a 0:15, abertura

"Olá! Neste vídeo vou demonstrar o REST."

0:15 a 1:15, teoria

[TELA] Slide 20 (a frase sobre o RPC e o REST).

"O professor comentou na aula que, em aplicações Web, o RPC perdeu espaço para a comunicação REST. REST é um estilo arquitetural, não um protocolo: tudo é um recurso, identificado por uma URL, e manipulado com os verbos do HTTP. É stateless: cada requisição carrega tudo de que o servidor precisa, e ele não guarda estado do cliente.

Nos eixos da aula, é síncrono, no modelo requisição e resposta com chamadas bloqueantes (slide 7). É transiente, confiável, por rodar sobre TCP, e discreto: cada requisição é uma mensagem completa."

1:15 a 3:00, demo

[TELA] Servidor à esquerda, cliente à direita. O servidor imprime os POST que recebe.

"Subo o servidor Flask e o cliente interativo.

Opção 1, POST: crio uma mensagem e o servidor responde 201, criado, com o id.

Opção 2, GET: listo as mensagens. Opção 3, GET por id: busco a de id 1.

Opção 4, PUT: edito o texto. Opção 5, DELETE: apago, e o servidor responde 204, sem conteúdo.

Agora, a opção 3 de novo com o id 1: 404, não encontrada. O código de status faz parte da comunicação."

[TELA] Abra um segundo terminal.

"Para mostrar a interoperabilidade, uso outra ferramenta, o curl, no mesmo servidor."
curl.exe localhost:5000/mensagens
"Não precisei de nenhum código meu: é só HTTP e JSON, então qualquer linguagem ou ferramenta consegue usar."

(No PowerShell, use curl.exe. O curl sem o .exe é um apelido de outro comando e se comporta diferente.)

3:00 a 3:30, fechamento

"Comparando com o gRPC: o REST é simples, universal e fácil de depurar, mas não tem um contrato formal como a IDL, e o JSON é mais pesado que o formato binário do gRPC. Obrigado!"