# REST - cliente envia mensagem ao servidor

    pip install -r requirements.txt
    python servidor.py     # terminal 1
    python cliente.py      # terminal 2

Tambem funciona com qualquer linguagem/ferramenta, pois e HTTP + JSON:

    curl -X POST localhost:5000/mensagens -H "Content-Type: application/json" -d '{"texto":"oi"}'
    curl localhost:5000/mensagens

Mostra verbos HTTP (POST/GET/PUT/DELETE), codigos de status (201, 400, 404, 204),
recursos identificados por URL e comunicacao stateless.
