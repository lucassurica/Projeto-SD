# Roteiro do vídeo — Kafka (≤ 5 min; use `./run.sh --auto`)

| Tempo | Demo | Falar |
|---|---|---|
| 0:00–0:40 | slide (README) | Kafka = log distribuído, particionado, replicado, append-only. Tópico, partição, offset, consumer group. Retenção independe de leitura. |
| 0:40–1:25 | 1 | 3 partições; **chave → partição** (mesma chave sempre na mesma partição); offsets; ordem só *dentro* da partição. Mostrar `kafka-topics --describe` (líder/ISR). |
| 1:25–2:50 | 2 | **Consumer group**: 1 consumidor pega as 3 partições; entra o 2º → rebalanceia; 3º → 1 cada; 4º → ocioso (limite = nº de partições); sai o 1º → o ocioso assume (failover). |
| 2:50–3:35 | 3 | Log **retido**: grupo `relatorios` lê tudo; relê → 0; grupo `antifraude` lê tudo de novo; **replay** a partir do offset 2. Mostrar `kafka-consumer-groups --describe` (LAG). |
| 3:35–4:00 | 4 | At-least-once (relê o 3) × at-most-once (perde o 3): o commit do offset define a garantia. |
| 4:00–5:00 | 5 | **Diferença p/ RabbitMQ**: mesmo cenário nos dois. RabbitMQ remove após ack → consumidor novo não acha nada; Kafka mantém → grupo novo lê as 5. Fechar com a tabela: carteiro × livro-razão; quando usar cada um. |
