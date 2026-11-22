# Roteiro do vídeo — RabbitMQ (≤ 5 min; é o mais denso, fale rápido e use `./run.sh --auto`)

Deixe o painel `localhost:15672` aberto (aba *Queues*) ao lado do terminal.

| Tempo | Demo | Falar |
|---|---|---|
| 0:00–0:25 | slide | Mensageria assíncrona: desacopla no tempo/espaço. Produtor → exchange → binding → fila → consumidor. |
| 0:25–1:20 | 1, 2, 3, 4 (rodar em `--auto 1 2 3 4`) | **direct** (exato; `debug` descartada), **fanout** (cópia p/ todas), **topic** (`*` e `#`, mostrar a matriz de quem recebeu o quê), **headers** (`x-match` all/any). |
| 1:20–2:00 | 5 | **Round-robin**: 6/6 mesmo com worker 10× mais lento. **Prefetch=1**: rápido faz 10, lento 2; tempo cai. |
| 2:00–2:30 | 6 | **Ponderado**: peso = nº de consumers → 12:4 e 3:6:9. |
| 2:30–3:30 | 7 | Persistente × transiente. Mostrar *publisher confirms*, restart do broker, e a tabela: só durável+persistente sobrevive. |
| 3:30–4:20 | 8 | Auto-ack perde ao cair; ack manual → `redelivered=True`. nack→DLQ. `mandatory` devolve msg não roteável. |
| 4:20–4:50 | 9 | Fila de prioridade vs FIFO. Prioridade só atua em backlog. |
| 4:50–5:00 | — | Fechar: RabbitMQ = roteamento rico + broker inteligente. (Próximo vídeo: Kafka.) |
