# Kafka x RabbitMQ

| Aspecto | RabbitMQ | Apache Kafka |
|---|---|---|
| Modelo | Broker de mensagens (filas + exchanges) | Log distribuido de eventos (topicos particionados) |
| Entrega | Broker EMPURRA (push) ao consumidor | Consumidor PUXA (pull) e controla o offset |
| Apos consumir | Mensagem removida da fila (apos ack) | Mensagem permanece (retencao por tempo/tamanho): permite replay |
| Roteamento | Rico: direct, fanout, topic, headers | Simples: topico + chave -> particao |
| Escala | Mais consumidores na fila (competing consumers) | Particoes + consumer groups; altissima vazao |
| Ordem | Por fila (se um consumidor) | Garantida por particao |
| Prioridade / TTL por mensagem | Suporta | Nao suporta nativamente |
| Casos de uso | Tarefas, RPC assincrono, roteamento complexo | Streaming, logs, event sourcing, big data, pipelines |
