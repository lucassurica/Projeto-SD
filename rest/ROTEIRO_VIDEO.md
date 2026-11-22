# Roteiro do vídeo — REST (≤ 5 min)

| Tempo | O que mostrar | O que falar |
|---|---|---|
| 0:00–0:50 | Slide/README: tabela de restrições | REST é estilo arquitetural, não protocolo. Stateless, cache, interface uniforme, camadas, HATEOAS. |
| 0:50–1:15 | `./demo.sh` | Servidor FastAPI + cliente Python na rede do Docker. |
| 1:15–2:00 | GET coleção, filtro, paginação, CSV | Recurso = substantivo/URI. `Link rel=next`, `X-Total-Count`. **Negociação de conteúdo** (`Accept`). |
| 2:00–2:50 | POST 201+Location, 409, 422 | Criar não é idempotente. Códigos de status comunicam o resultado. |
| 2:50–3:30 | GET + ETag → 304 | Cache condicional economiza banda: servidor não reenvia o corpo. |
| 3:30–4:10 | PUT ×2, PATCH, DELETE ×2 | Idempotência: PUT/DELETE repetidos → mesmo estado. DELETE: 204 depois 404. |
| 4:10–4:30 | 401 sem `X-API-Key` | Stateless: a credencial viaja em toda requisição. |
| 4:30–5:00 | Parte `curl` + abrir `localhost:8000/docs` | Qualquer linguagem/cliente HTTP consome; OpenAPI gera docs e SDKs. Comparar rapidamente com gRPC. |
