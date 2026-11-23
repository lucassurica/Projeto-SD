# Apache Kafka - confluent-kafka

Cada demo usa 2+ terminais. Em todos eles, entre na pasta `kafka` (no terminal: cd kafka/).

## 0. Preparar (uma vez)
    docker compose up -d
    pip install -r requirements.txt
    # rode docker compose up -d novamente caso não tenha funcionado na primeira vez
    python criar_topico.py                 # cria o topico 'mensagens' com 3 particoes

## 1. Enviar e receber (particoes e chaves)
# Suba o consumidor primeiro e espere uns 5 a 10 segundos (ele precisa entrar no grupo antes de receber):

    python consumidor.py g1                # terminal 1: fica aguardando
    python produtor.py                     # terminal 2: envia 9 mensagens

## 2. Replay (a mensagem nao some depois de lida)
# Um grupo NOVO le o topico inteiro desde o inicio:

    python consumidor.py g2                # terminal 1

## 3. Balanceamento: particoes divididas dentro de um grupo
# Dois consumidores com o MESMO grupo dividem as particoes entre si. Use um grupo novo (g3):

    python consumidor.py g3                # terminal 1
    python consumidor.py g3                # terminal 2 (espere uns 5 a 10 segundos, o Kafka redistribui as particoes)
    python produtor.py                     # terminal 3

## Se quiser uma demonstração só com mensagens novas, rode os comandos abaixo, e volte para o que quer testar
    docker compose down
    docker compose up -d
    python criar_topico.py
