# Projeto de Sistemas Distribuídos — Protocolos de Comunicação

Demonstração de quatro protocolos/modelos de comunicação distribuída. Cada pasta é **independente**
(tem `docker-compose.yml`, `demo.sh`/`run.sh`, README com a teoria e roteiro de vídeo de ≤ 5 min).
Tudo em **Python**, executado em **containers Docker** numa única máquina (distribuição lógica, via rede,
não geográfica). O host precisa apenas de Docker + Docker Compose.

| Pasta | Protocolo | Estilo de comunicação | Comando |
|---|---|---|---|
| [`grpc/`](grpc) | gRPC (HTTP/2 + Protobuf) | RPC síncrono; unário e 3 tipos de streaming | `./demo.sh` |
| [`rest/`](rest) | REST (HTTP + JSON) | Requisição/resposta sobre recursos | `./demo.sh` |
| [`rabbitmq/`](rabbitmq) | RabbitMQ (AMQP) | Mensageria assíncrona com filas e roteamento | `./run.sh` |
| [`kafka/`](kafka) | Apache Kafka | Log de eventos particionado (streaming) | `./run.sh` |

## Comparação geral

| | REST | gRPC | RabbitMQ | Kafka |
|---|---|---|---|---|
| Acoplamento | temporal (síncrono) | temporal (síncrono) | **desacoplado** | **desacoplado** |
| Paradigma | recurso/CRUD | chamada de procedimento | fila + roteamento | log de eventos |
| Formato | JSON (texto) | Protobuf (binário) | qualquer (bytes) | qualquer (bytes) |
| Contrato | OpenAPI (opcional) | `.proto` (obrigatório) | implícito | implícito (+ Schema Registry) |
| Streaming | limitado | nativo (4 modos) | contínuo via consumers | nativo, com replay |
| Garante ordem | n/a | por stream | por fila | por partição |
| Ideal para | APIs públicas | microsserviços internos | tarefas, workflows | eventos, dados em volume |

## Mensageiro simples (cliente envia mensagens ao servidor)
Em cada pasta, em dois terminais:
```bash
./mensagens.sh servidor    # terminal 1
./mensagens.sh cliente     # terminal 2 — digite mensagens; /sair encerra
```

## Gerar os .zip para entrega (um por protocolo)
```bash
python3 make_zips.py        # cria dist/grpc.zip, dist/rest.zip, dist/rabbitmq.zip, dist/kafka.zip
```
Os **vídeos** (≤ 5 min cada, um por protocolo) devem ser gravados seguindo o `ROTEIRO_VIDEO.md`
de cada pasta e enviados ao Classroom como arquivos individuais (sem links, sem compactar).
