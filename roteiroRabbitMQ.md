RabbitMQ, parte 1: roteamento e balanceamento (~5 min)
0:00 a 0:20, abertura

[TELA] Terminal vazio.

"Olá! Neste vídeo vou demonstrar o RabbitMQ. Na parte 1, o roteamento de mensagens com todos os tipos de exchange e o balanceamento de carga. Na parte 2, persistência, confirmação de recebimento e prioridade."

0:20 a 1:30, teoria

[TELA] Slide 81 (a figura do RabbitMQ) ou um desenho seu de produtor, exchange, fila e consumidor.

"O RabbitMQ é um middleware orientado a mensagens, um MOM. Nos eixos que vimos na aula, a comunicação é assíncrona: o remetente continua executando logo depois de enviar. É persistente, porque a mensagem fica guardada na fila até ser retirada, mesmo que o receptor não esteja rodando. Por isso o acoplamento é fraco em relação ao tempo.

Ele implementa o protocolo AMQP e funciona como um message broker: um intermediário que cuida do roteamento, do armazenamento e da entrega.

A diferença importante é a exchange. O produtor não coloca a mensagem direto na fila: ele a entrega à exchange. A exchange nunca armazena mensagens. Ela só decide, pelas regras de binding, para quais filas a mensagem vai. Quem guarda é a fila. Existem quatro tipos de exchange, e vou demonstrar todos."

1:30 a 3:30, roteamento

[TELA] Dois terminais: consumidor à esquerda, produtor à direita. Para cada tipo, rode o consumidor, depois o produtor, e dê Ctrl+C no consumidor antes do próximo.

Direct (python roteamento_consumidor.py direct erro, depois python roteamento_produtor.py direct)

"Na direct, a chave precisa ser exatamente igual. Meu consumidor se vinculou à chave erro. O produtor envia três mensagens: info, erro e aviso. Só a de erro chega."

Fanout (dois consumidores fanout, depois o produtor)

"Na fanout, a exchange ignora a chave e envia para todas as filas vinculadas. Com dois consumidores, os dois recebem as três mensagens."

Topic (python roteamento_consumidor.py topic "*.erro")

"Na topic, a vinculação usa padrões, com asterisco e jogo da velha. O padrão *.erro casa com pagamento.erro e estoque.erro, e ignora pagamento.ok."

Headers (python roteamento_consumidor.py headers formato=pdf tipo=relatorio)

"O quarto tipo, que a aula não detalha mas o AMQP suporta, é o headers. Aqui o roteamento não usa a chave, e sim os cabeçalhos da mensagem. O produtor envia um documento PDF e um CSV, e só o PDF casa com as duas condições."

3:30 a 5:00, balanceamento

[TELA] Três terminais. Suba os consumidores primeiro e o produtor depois.

Round-robin (balanceamento_consumidor.py A, balanceamento_consumidor.py B, depois balanceamento_produtor.py 12)

"Para o balanceamento, dois consumidores leem a mesma fila. Por padrão o RabbitMQ distribui em round-robin, alternando entre eles. Das 12 tarefas, 6 vão para cada um."

Ponderado (balanceamento_consumidor.py A --peso 3, balanceamento_consumidor.py B --peso 1, depois balanceamento_produtor.py 12)

"O RabbitMQ não tem ponderação nativa, então implementei assim: o consumidor A registra três consumidores na mesma fila, e o B registra um. Como o broker alterna entre consumidores, A recebe três mensagens para cada uma de B. Das 12, 9 vão para A e 3 para B. É um round-robin ponderado."

"Resumindo a parte 1: a exchange decide o destino, a fila guarda, e os consumidores dividem a carga. Na parte 2, vemos persistência, confirmação e prioridade."

RabbitMQ, parte 2: persistência, confirmação e prioridade (~5 min)
0:00 a 0:15, abertura

"Esta é a parte 2 do RabbitMQ. Vou mostrar comunicação persistente e transiente, com e sem confirmação de recebimento, e uso de prioridade nas filas."

0:15 a 2:15, persistente × transiente

[TELA] Terminal e painel do RabbitMQ (localhost:15672, aba Queues).

Primeiro nível, a fila guarda (balanceamento_produtor.py 5 sem nenhum consumidor)

"Na aula, a figura 4.15 mostra o caso em que o remetente está ativo e o receptor está passivo. Vou reproduzir: enviei 5 tarefas e não há nenhum consumidor rodando. No painel, elas aparecem como prontas na fila. Agora subo o consumidor (balanceamento_consumidor.py A), e ele recebe tudo. O receptor não precisava estar ativo quando a mensagem foi enviada: isso é comunicação persistente, e é o que o MOM garante."

Segundo nível, sobreviver ao broker (python persistencia.py enviar, reinício do broker, python persistencia.py ler)

"Mas e se o próprio broker cair? O AMQP prevê mensagens marcadas como duráveis. Enviei duas mensagens: a primeira para uma fila durável, com delivery_mode persistente, gravada em disco. A segunda, transiente, para uma fila não durável, só em memória. Agora reinicio o broker."

[TELA] Em PowerShell, docker compose restart rabbitmq. Corte a espera na edição.

"Lendo as duas filas: a persistente continua lá, e a transiente foi perdida."

2:15 a 4:15, com e sem confirmação

[TELA] Painel das filas aberto ao lado, para mostrar a contagem.

Do lado do produtor (python confirmacao_produtor.py)

"Do lado do produtor, ativei os publisher confirms: o broker confirma cada mensagem que recebeu. Aqui os cinco pedidos foram confirmados. E se eu enviar para uma fila que não existe, a mensagem volta para o produtor, que fica sabendo da falha."

Do lado do consumidor, sem confirmação (confirmacao_consumidor.py auto --falhar)

"No consumidor, o primeiro modo é sem confirmação, o auto ack: o broker considera a mensagem entregue assim que a envia. O consumidor recebe os pedidos 1 e 2 e, ao chegar no 3, cai. Olhem o painel: a fila está vazia. Os pedidos 3, 4 e 5 foram perdidos."

Com confirmação (reenvie com confirmacao_produtor.py, depois confirmacao_consumidor.py manual --falhar)

"Reenvio os pedidos e agora uso o modo com confirmação: o consumidor só dá o ack depois de processar. Ele confirma o 1 e o 2 e cai no 3. Desta vez, as mensagens sem ack voltam para a fila. Subo o consumidor de novo (confirmacao_consumidor.py manual), e ele recebe o 3, o 4 e o 5 com redelivered verdadeiro."

"Isso se liga ao AMQP: a mensagem só passa ao estado resolvido quando o receptor informa que concluiu o processamento. É a confiabilidade de ponta a ponta que o professor destacou."

4:15 a 5:00, prioridade e fechamento

[TELA] python prioridade.py enviar e depois python prioridade.py ler.

"Por fim, a prioridade. A fila é declarada com prioridade máxima 10. Enviei dez mensagens em ordem embaralhada, sem consumidor. Ao ler, saem primeiro as de prioridade 9, 8, 7, até a 0: a ordem de leitura é definida pela prioridade, não pela ordem de chegada."

"Para fechar: o RabbitMQ oferece roteamento flexível por exchanges, balanceamento entre consumidores, garantias de entrega configuráveis e prioridade, tudo desacoplando produtor e consumidor no tempo. Obrigado!"