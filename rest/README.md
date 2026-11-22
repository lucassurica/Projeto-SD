# REST — API do Armazém

Servidor **FastAPI** (Python) + cliente **Python** (`requests`) + exemplos com **`curl`**
(prova de que qualquer cliente HTTP, em qualquer linguagem, consome a API).

```bash
./demo.sh            # sobe a API, roda o cliente Python e depois chamadas curl
docker compose down
```
Swagger UI interativo: <http://localhost:8000/docs> (com a API no ar).
Chave de API usada nos exemplos: header `X-API-Key: segredo-sd`.

## Teoria

**REST** (*Representational State Transfer*, Fielding, 2000) é um **estilo arquitetural** — não um
protocolo — normalmente implementado sobre HTTP. As restrições:

| Restrição | Como aparece aqui |
|---|---|
| **Cliente–servidor** | separação de responsabilidades; a API evolui independente do front |
| **Sem estado (stateless)** | cada requisição traz a credencial (`X-API-Key`); nada de sessão no servidor → escala horizontal fácil |
| **Cache** | `ETag`/`If-None-Match` → **304 Not Modified**; `Cache-Control: max-age` |
| **Interface uniforme** | recursos com URI (`/v1/produtos/6`), verbos padrão, representações (JSON/CSV), **HATEOAS** (`_links`) |
| **Sistema em camadas** | proxies, CDNs e gateways ficam transparentes |
| **Código sob demanda** (opcional) | não usado |

### Verbos, semântica e status (todos demonstrados)
| Verbo | Uso | Seguro | Idempotente | Resposta típica |
|---|---|---|---|---|
| GET | ler | ✔ | ✔ | 200, **304**, 404 |
| POST | criar | ✘ | ✘ | **201 + `Location`**, 409, 422 |
| PUT | substituir inteiro | ✘ | ✔ | 200 (2 chamadas = mesmo resultado) |
| PATCH | alterar parcialmente | ✘ | (depende) | 200 |
| DELETE | remover | ✘ | ✔ | **204** (repetir → 404) |
| OPTIONS | descobrir métodos | ✔ | ✔ | 204 + `Allow` |

Classes de status: 2xx sucesso · 3xx redirecionamento/cache · 4xx erro do cliente (401, 404, 409, 422) · 5xx erro do servidor.

### Outras características
- **Negociação de conteúdo**: `Accept: text/csv` vs `application/json` para o mesmo recurso.
- **Paginação + filtros**: `?categoria=…&limite=…&pagina=…`, com `Link: <…>; rel="next"` e `X-Total-Count`.
- **Versionamento**: prefixo `/v1/`.
- **Validação** declarativa (Pydantic) → 422 com detalhes.
- **OpenAPI** gerada automaticamente (`/openapi.json`, `/docs`) — contrato legível por máquina, base para gerar SDKs em qualquer linguagem.

### Interoperabilidade
HTTP + JSON são universais: browser, mobile, `curl`, qualquer linguagem com biblioteca HTTP.
É o que torna REST o padrão para **APIs públicas**. O custo: JSON é verboso, sem tipagem forte nativa,
*over/under-fetching*, e não há streaming bidirecional nativo (ver comparação em `../grpc/README.md`).

## Mensageiro simples (cliente → servidor)
`POST /v1/mensagens` com `{"remetente": ..., "texto": ...}` → `201 Created`; `GET /v1/mensagens` lista o histórico (`/listar` no cliente).
```bash
./mensagens.sh servidor    # terminal 1: mostra as mensagens recebidas
./mensagens.sh cliente     # terminal 2: pede o nome e depois cada linha digitada vira um POST
```
Código: `client/mensagem_client.py` e os endpoints `/v1/mensagens` em `server/app.py`.

## Estrutura
```
server/app.py      API FastAPI (todas as características)
client/client.py   cliente Python que percorre cada característica
demo.sh            cliente Python + curl
```
