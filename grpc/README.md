# gRPC — Sistema de Armazém

Servidor e cliente em **Python**, gerados a partir de **um único contrato `.proto`**.
Tudo roda em containers numa só máquina (`docker compose`); a distribuição é lógica (processos
isolados que só se falam pela rede), não geográfica.

```bash
./demo.sh            # sobe o servidor, roda o cliente e mostra o log do servidor
docker compose down  # encerrar
```

Requisitos: Docker + Docker Compose. Nada é instalado no host.

## Teoria

**RPC (Remote Procedure Call)** faz uma chamada remota parecer uma chamada de função local:
o *stub* do cliente serializa os argumentos (*marshalling*), envia pela rede, e o *skeleton* do
servidor executa e devolve o resultado. O gRPC é o RPC moderno do Google (CNCF).

| Pilar | O que é | Por que importa |
|---|---|---|
| **Protocol Buffers** | IDL + serialização binária. Campos têm número (`id = 1`) | Mensagens 3–10× menores que JSON; evolução compatível (adicionar campos novos não quebra clientes antigos); tipagem forte |
| **HTTP/2** | Transporte: multiplexação de vários streams numa conexão TCP, frames binários, compressão de cabeçalhos, *full-duplex* | Habilita os 4 tipos de streaming e baixa latência |
| **Geração de código** | `protoc` gera stubs a partir do `.proto` para ~12 linguagens (Python, Java, Go, C++, C#, Node, Kotlin, Dart, Ruby, PHP, Swift…) | **Interoperabilidade**: um serviço em Go é chamado por um cliente Java sem escrever parser algum — o contrato é a fonte da verdade |

### Os 4 tipos de chamada (todos demonstrados)

| Tipo | Assinatura no `.proto` | Demo |
|---|---|---|
| Unário | `rpc ConsultarProduto(Req) returns (Res)` | consulta um produto |
| Server streaming | `returns (stream Produto)` | lista de produtos chegando aos poucos |
| Client streaming | `rpc ImportarProdutos(stream Produto) returns (Resumo)` | envio em lote → 1 resumo |
| Bidirecional | `rpc Negociar(stream Oferta) returns (stream Contraoferta)` | negociação de preço em tempo real |

### Outras características demonstradas
- **Metadata** (≈ headers HTTP): `authorization` enviado pelo cliente; `x-servidor` (inicial) e `x-tempo-ms` (*trailer*) devolvidos pelo servidor.
- **Interceptor** no servidor (`AuthInterceptor`): middleware que valida o token nos 4 tipos de RPC.
- **Códigos de status** próprios do gRPC: `NOT_FOUND`, `UNAUTHENTICATED`, `DEADLINE_EXCEEDED` (não são códigos HTTP).
- **Deadline/timeout propagado**: o cliente dá 1 s; o servidor percebe (`context.is_active()`) e interrompe o trabalho — evita desperdício e falhas em cascata.
- **Cancelamento** de streams pelo cliente.

### Quando usar / quando evitar
✅ Microsserviços internos, baixa latência, streaming, poliglota, contratos rígidos.
⚠️ Navegadores não falam gRPC nativo (precisa de gRPC-Web/proxy); payload binário não é legível (`curl` não serve; use `grpcurl`); menos cache/ferramental HTTP que REST.

### gRPC × REST (resumo; ver também `../rest`)
| | gRPC | REST |
|---|---|---|
| Contrato | `.proto` obrigatório | opcional (OpenAPI) |
| Formato | binário (protobuf) | texto (JSON) |
| Transporte | HTTP/2 | HTTP/1.1 ou 2 |
| Streaming | nativo, 4 modos | limitado (SSE/WebSocket) |
| Estilo | orientado a **ações** (verbos) | orientado a **recursos** (substantivos) |

### Interoperabilidade na prática
Para criar um cliente em **outra linguagem** basta copiar `proto/armazem.proto` e gerar os stubs, sem mexer no servidor:
```bash
# Go
protoc --go_out=. --go-grpc_out=. proto/armazem.proto
# Java / Node / C# ... mesma ideia com o plugin da linguagem
```
(Nesta entrega servidor e cliente são ambos Python, por escolha do grupo; o argumento de
interoperabilidade vem do fato de o `.proto` ser neutro e de a wire format ser padronizada.)

## Mensageiro simples (cliente → servidor)
Chamada unária `Mensageiro.Enviar(Mensagem) returns (Confirmacao)` definida no mesmo `proto/armazem.proto`.
O servidor imprime cada mensagem e o cliente recebe uma confirmação síncrona (nº e hora).
```bash
./mensagens.sh servidor    # terminal 1: mostra as mensagens recebidas
./mensagens.sh cliente     # terminal 2: pede o nome e depois cada linha digitada é enviada
```
Código: `client/mensagem_client.py` e `MensageiroServicer` em `server/server.py`.

## Estrutura
```
proto/armazem.proto     contrato único
server/server.py        4 RPCs + interceptor + metadata + deadline
client/client.py        percorre todas as características
docker-compose.yml, demo.sh, ROTEIRO_VIDEO.md
```
