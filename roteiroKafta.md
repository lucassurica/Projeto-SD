Vídeo Kafka (~4 min)
0:00 a 0:15, abertura

"Olá! Neste vídeo vou demonstrar o Apache Kafka e explicar a diferença em relação ao RabbitMQ."

0:15 a 1:45, teoria e comparação

[TELA] A tabela do KAFKA_vs_RABBITMQ.md.

"O Kafka também é um sistema de mensagens com comunicação assíncrona e persistente, mas funciona de forma bem diferente do RabbitMQ. Vale avisar que o Kafka não está nos slides da aula. As informações vêm da documentação oficial.

O RabbitMQ é um MOM, como o da aula: um broker com exchanges e filas, que empurra as mensagens para os consumidores. Depois do ack, a mensagem sai da fila. O roteamento é rico, com direct, fanout, topic e headers.

O Kafka é um log distribuído. As mensagens são gravadas em tópicos, divididos em partições, e cada mensagem tem um offset, a sua posição. O consumidor puxa as mensagens e controla até onde leu, de um jeito parecido com o poll que vimos na interface de filas. E a mensagem não some depois de lida: ela fica pelo tempo de retenção configurado, então dá para reler.

Consequência prática: o RabbitMQ é ótimo para distribuir tarefas e fazer roteamento complexo, e o Kafka é ideal para fluxos de eventos, logs e alto volume de dados."

1:45 a 3:45, demo

[TELA] Painéis lado a lado.

"Primeiro crio o tópico com 3 partições." python criar_topico.py

"Subo um consumidor do grupo g1." python consumidor.py g1

"Agora o produtor envia 9 mensagens, cada uma com uma chave." python produtor.py

"Repare na saída do produtor: cada mensagem foi para uma partição e ganhou um offset. A mesma chave sempre cai na mesma partição, o que preserva a ordem por chave. O consumidor recebeu tudo."

[TELA] Abra dois consumidores g1, espere uns 10 segundos e rode o produtor de novo.

"Agora dois consumidores no mesmo grupo. O Kafka divide as partições entre eles: cada partição é lida por um só consumidor do grupo, então eles dividem o trabalho."

[TELA] python consumidor.py g2

"Por último, o replay. Um grupo novo, g2, começa do início e recebe todas as mensagens de novo. No RabbitMQ, uma mensagem já consumida não existe mais. No Kafka, ela continua no log."

3:45 a 4:10, fechamento

"Em resumo: RabbitMQ é um broker de filas, que entrega e remove, com roteamento flexível. O Kafka é um log particionado, com leitura por offset, replay e alta vazão. Obrigado!"