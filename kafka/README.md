# Apache Kafka — Log distribuído de eventos

Broker `apache/kafka:3.9.0` em **modo KRaft** (sem ZooKeeper) + demos em **Python (confluent-kafka)**.

```bash
./run.sh                 # todas as demos, com pausa (ENTER)
./run.sh --auto          # sem pausas
./run.sh --auto 2        # só a demo 2
docker compose --profile comparacao down -v   # encerrar
```

## Teoria

Kafka é uma **plataforma de streaming de eventos**: em vez de "filas", é um **log distribuído,
particionado, replicado e só de acrescentar (append-only)**. Mensagens (*records*) ficam gravadas em disco
por um período de **retenção** (padrão 7 dias), **independentemente de terem sido lidas**.

| Conceito | Definição |
|---|---|
| **Tópico** | categoria/nome do fluxo de eventos (`pedidos`) |
| **Partição** | fatia ordenada e imutável do tópico; é a unidade de **paralelismo** e de **ordem** |
| **Offset** | posição de um record dentro da partição (0, 1, 2…) |
| **Chave** | `hash(chave) % nº partições` escolhe a partição → mesma chave = mesma partição = ordem preservada |
| **Consumer group** | conjunto de consumidores que **dividem** as partições; cada partição → no máximo 1 consumidor do grupo |
| **Offset commit** | cada grupo guarda até onde leu; o *consumidor* (pull) controla a leitura |
| **Replicação** | cada partição tem líder + seguidores (ISR); tolerância a falha de broker (aqui, 1 broker → fator 1) |

### Demos
| # | Arquivo | Mostra |
|---|---|---|
| 1 | `k1_particoes_chaves.py` | tópico com 3 partições; chave → partição; offsets; ordem por chave; `kafka-topics --describe` |
| 2 | `k2_grupos_consumidores.py` | consumer group: 1→2→3→4 consumidores, **rebalanceamento**, consumidor ocioso, failover |
| 3 | `k3_replay_offsets.py` | log retido: vários grupos leem tudo; **replay** por offset; retenção; LAG via CLI |
| 4 | `k4_semanticas_entrega.py` | **at-least-once** × **at-most-once** (momento do commit); produtor idempotente |
| 5 | `k5_comparacao_rabbitmq.py` | **mesmo cenário nos dois brokers** + tabela comparativa |

### Garantias de entrega
- **At-most-once**: commit *antes* de processar → crash perde a mensagem (demo 4).
- **At-least-once** (padrão recomendado): commit *depois* → crash reprocessa → processamento deve ser **idempotente**.
- **Exactly-once**: produtor idempotente (`enable.idempotence`) + transações; vale dentro do Kafka (consumir→processar→produzir).
- `acks=all` no produtor: o líder só confirma após todas as réplicas em sincronia gravarem.

## Kafka × RabbitMQ — a diferença

> **RabbitMQ é um *carteiro* (entrega a mensagem e a descarta). Kafka é um *livro-razão* (registra tudo e cada leitor guarda o marcador de onde parou).**

| Aspecto | RabbitMQ | Kafka |
|---|---|---|
| Modelo | Fila; broker **inteligente** (roteia, prioriza, rastreia ack por mensagem) | Log; broker **simples**, consumidor **inteligente** (guarda offset) |
| Após consumir | Mensagem **removida** (ack) | Mensagem **retida** pelo tempo de retenção |
| Releitura / replay | ✘ | ✔ (seek por offset, novo grupo desde o início) |
| Entrega | *Push* ao consumidor | *Pull* pelo consumidor |
| Roteamento | Rico: direct, fanout, topic, headers | Só tópico + chave de partição |
| Vários destinatários | Fanout / uma fila por assinante | Um **consumer group** por assinante, sobre o mesmo log (sem copiar dados) |
| Escala do consumo | Vários consumidores na mesma fila | Consumidores ≤ nº de partições |
| Ordem | Por fila (se 1 consumidor) | Por partição |
| Prioridade, TTL por msg, DLQ | Nativos | Não nativos (implementar na aplicação) |
| Throughput | ~10⁴–10⁵ msg/s | ~10⁵–10⁶+ msg/s (escrita sequencial em disco, *batching*, zero-copy) |
| Melhor para | Tarefas/jobs, RPC assíncrono, workflows, roteamento complexo | Streaming, *event sourcing*, pipelines de dados/ETL, logs, reprocessamento |

**Regra prática:** precisa *distribuir tarefas* com roteamento e prioridade → RabbitMQ.
Precisa de *histórico de eventos*, vários consumidores independentes e altíssimo volume → Kafka.
A demo 5 prova a diferença central: 5 mensagens são lidas e confirmadas; um consumidor **novo** não acha nada no RabbitMQ, mas lê as 5 no Kafka.

## Mensageiro simples (cliente → servidor)
O cliente grava cada linha no tópico `mensagens` (chave = nome do remetente); o "servidor" é um consumidor do grupo `servidor-mensagens` e mostra partição/offset.
O log retém as mensagens: um servidor que sobe depois lê tudo desde o início.
```bash
./mensagens.sh servidor    # terminal 1: consumidor
./mensagens.sh cliente     # terminal 2: produtor
```
Código: `demos/chat_cliente.py` e `demos/chat_servidor.py`.

## Estrutura
```
docker-compose.yml  kafka (KRaft) + cliente + rabbitmq (profile "comparacao", só demo 5)
demos/              common.py, k1…k5
run.sh, ROTEIRO_VIDEO.md
```
