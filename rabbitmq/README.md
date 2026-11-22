# RabbitMQ — Mensageria com AMQP 0-9-1

Broker `rabbitmq:4-management` + demos em **Python (pika)**. Painel web: <http://localhost:15672> (`guest`/`guest`).

```bash
./run.sh                 # todas as demos, com pausa (ENTER) entre elas — ideal p/ gravar
./run.sh --auto          # sem pausas
./run.sh --auto 3 6      # só as demos 3 e 6
docker compose down -v   # encerrar
```

## Teoria

**Comunicação assíncrona por mensagens**: produtor e consumidor não precisam estar no ar ao mesmo
tempo (*desacoplamento temporal*), nem se conhecer (*desacoplamento espacial*). O broker guarda a
mensagem até alguém consumir. Ganhos: absorver picos (buffer), tolerância a falhas, escalar consumidores.

**Modelo AMQP:** `Produtor → Exchange →(binding + routing key)→ Fila → Consumidor`.
O produtor **nunca** publica direto na fila: publica numa *exchange*, que decide para quais filas copiar a mensagem.

| # | Demo | O que prova |
|---|---|---|
| 1 | `01_direct.py` | **Direct**: routing key = binding key (exato). + exchange padrão `""` |
| 2 | `02_fanout.py` | **Fanout**: broadcast p/ todas as filas (pub/sub) |
| 3 | `03_topic.py` | **Topic**: padrões `*` (1 palavra) e `#` (0+ palavras) |
| 4 | `04_headers.py` | **Headers**: roteia por atributos, `x-match=all/any` |
| 5 | `05_round_robin.py` | **Round-robin** e **despacho justo** (`prefetch=1`) |
| 6 | `06_round_robin_ponderado.py` | **Round-robin ponderado** 3:1 e 1:2:3 |
| 7 | `07_persistencia.py` | **Persistente × transiente**, com *publisher confirms*, sobrevivendo a restart do broker |
| 8 | `08_confirmacoes.py` | **Com × sem ack**: auto-ack perde, ack manual reentrega; nack→DLQ; confirms/mandatory do produtor |
| 9 | `09_prioridade.py` | **Fila de prioridade** (`x-max-priority`) vs FIFO |

### Tipos de roteamento (exchange)
| Tipo | Regra | Exemplo na demo |
|---|---|---|
| direct | chave exata | `error` → `q_erros` e `q_tudo`; `debug` (sem binding) é descartada |
| fanout | ignora chave; copia p/ todas | 1 evento → e-mail, SMS e auditoria |
| topic | padrão com `*` e `#` | `pedido.sp.criado` casa com `pedido.*.criado`, `pedido.#`, `*.sp.*`, `#` |
| headers | casa cabeçalhos | `doc1{pdf,alta}` → `q_pdf_urgente` (all) e `q_pdf_ou_web` (any) |
| default (`""`) | direct implícito: chave = nome da fila | envio direto por nome de fila |

### Balanceamento de carga entre consumidores (*competing consumers*)
- **Round-robin (padrão):** a fila entrega 1 mensagem a cada consumidor, em ciclo, *sem olhar a carga*. Na demo 5, o worker 10× mais lento recebe 6 de 12, igual ao rápido.
- **Despacho justo:** `basic_qos(prefetch_count=1)` → só entrega a próxima após o ack da anterior; o worker rápido atende mais (10 contra 2) e o tempo total cai (1,2 s → 0,4 s).
- **Round-robin ponderado:** o RabbitMQ não tem "peso" nativo — usa-se o fato de o round-robin ser **por consumidor**: um worker com peso *w* registra *w* consumers na fila. Pesos A=3, B=1 → 12 e 4 de 16 mensagens (3:1).

### Persistência × transiente; com × sem confirmação
Para uma mensagem sobreviver a um restart do broker são necessárias **as duas** coisas:
1. **Fila durável** (`durable=True`) e 2. **mensagem persistente** (`delivery_mode=2`).

| Fila | Mensagem | Após restart (demo 7) |
|---|---|---|
| durável | persistente | ✔ 3 mensagens |
| durável | transiente | fila existe, **0** mensagens |
| não durável | persistente | fila **desapareceu** |

*Observação:* o RabbitMQ 4.x **deprecou** filas transientes não exclusivas; por isso `rabbitmq.conf`
reabilita `transient_nonexcl_queues` — o suficiente para demonstrar o contraste.

Três "confirmações" diferentes (não confundir):
- **Consumer ack** (`basic_ack`): consumidor → broker "processei". Sem ele (auto-ack) uma queda perde a mensagem; com ele há **reentrega** (`redelivered=True`) → semântica *at-least-once*.
- **Publisher confirm** (`confirm_delivery`): broker → produtor "recebi e (se persistente) gravei em disco".
- **`mandatory` / `basic.return`**: broker devolve ao produtor mensagem que **não casou com nenhuma fila**.
- **`nack(requeue=False)` + DLX**: rejeitada vai para a *Dead Letter Queue* (cabeçalho `x-death` com motivo).

### Prioridade
Fila declarada com `x-max-priority=10`; mensagem leva `priority=0..10`. A fila entrega primeiro as mais prioritárias
(demo 9: fraude(10) → pagamento(9) → … → backup(1)); a fila comum é FIFO. A prioridade só **reordena o que está
esperando** (backlog); com consumidor ocioso a mensagem é entregue na hora. Quanto maior o máximo, mais custo (uma sub-fila interna por nível).

## Estrutura
```
docker-compose.yml  rabbitmq:4-management + container cliente (profile "clients")
rabbitmq.conf       reabilita filas transientes (deprecadas no 4.x)
demos/              common.py, balanceamento.py, 01…09
run.sh              orquestra as demos (inclui o restart do broker na demo 7)
ROTEIRO_VIDEO.md
```
