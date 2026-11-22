"""API REST (FastAPI) — demonstra verbos HTTP, códigos de status, recursos,
idempotência, paginação, filtros, cache condicional (ETag), HATEOAS,
versionamento, negociação de conteúdo, autenticação e OpenAPI."""
import hashlib
import json
import os
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

API_KEY = os.getenv("API_KEY", "segredo-sd")

app = FastAPI(title="Armazém REST", version="1.0",
              description="API REST didática — disciplina de Sistemas Distribuídos")


class ProdutoIn(BaseModel):
    nome: str = Field(min_length=1)
    categoria: str
    preco: float = Field(gt=0)
    estoque: int = Field(ge=0, default=0)


class ProdutoPatch(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=1)
    categoria: Optional[str] = None
    preco: Optional[float] = Field(default=None, gt=0)
    estoque: Optional[int] = Field(default=None, ge=0)


DB = {
    1: {"id": 1, "nome": "Notebook", "categoria": "ELETRONICOS", "preco": 4500.0, "estoque": 10},
    2: {"id": 2, "nome": "Fone Bluetooth", "categoria": "ELETRONICOS", "preco": 250.0, "estoque": 40},
    3: {"id": 3, "nome": "Sistemas Distribuídos", "categoria": "LIVROS", "preco": 120.0, "estoque": 15},
    4: {"id": 4, "nome": "Clean Code", "categoria": "LIVROS", "preco": 95.0, "estoque": 8},
    5: {"id": 5, "nome": "Café Especial 1kg", "categoria": "ALIMENTOS", "preco": 65.0, "estoque": 100},
}
proximo_id = 6


def autenticar(x_api_key: Optional[str] = Header(default=None)):
    """Autenticação sem estado (stateless): toda requisição traz a credencial."""
    if x_api_key != API_KEY:
        raise HTTPException(401, "X-API-Key ausente ou inválida",
                            headers={"WWW-Authenticate": "ApiKey"})


def etag_de(obj) -> str:
    return '"' + hashlib.md5(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:12] + '"'


def com_links(p: dict) -> dict:
    """HATEOAS: o recurso informa o que se pode fazer a seguir."""
    return {**p, "_links": {
        "self": {"href": f"/v1/produtos/{p['id']}", "method": "GET"},
        "atualizar": {"href": f"/v1/produtos/{p['id']}", "method": "PUT"},
        "remover": {"href": f"/v1/produtos/{p['id']}", "method": "DELETE"},
        "colecao": {"href": "/v1/produtos", "method": "GET"},
    }}


@app.get("/saude", tags=["infra"])
def saude():
    return {"status": "ok"}


# GET /v1/produtos — coleção, com filtro + paginação + negociação de conteúdo
@app.get("/v1/produtos", tags=["produtos"], dependencies=[Depends(autenticar)])
def listar(request: Request, response: Response,
           categoria: Optional[str] = None, preco_max: Optional[float] = None,
           limite: int = Query(2, ge=1, le=50), pagina: int = Query(1, ge=1)):
    itens = [p for p in DB.values()
             if (categoria is None or p["categoria"] == categoria.upper())
             and (preco_max is None or p["preco"] <= preco_max)]
    total = len(itens)
    ini = (pagina - 1) * limite
    fatia = itens[ini:ini + limite]
    links = []
    base = f"/v1/produtos?limite={limite}"
    if categoria:
        base += f"&categoria={categoria}"
    if ini + limite < total:
        links.append(f'<{base}&pagina={pagina + 1}>; rel="next"')
    if pagina > 1:
        links.append(f'<{base}&pagina={pagina - 1}>; rel="prev"')
    headers = {"X-Total-Count": str(total)}
    if links:
        headers["Link"] = ", ".join(links)

    # Negociação de conteúdo: mesmo recurso, representações diferentes (Accept)
    if "text/csv" in request.headers.get("accept", ""):
        csv = "id,nome,categoria,preco,estoque\n" + "\n".join(
            f"{p['id']},{p['nome']},{p['categoria']},{p['preco']},{p['estoque']}" for p in fatia)
        return PlainTextResponse(csv, media_type="text/csv", headers=headers)
    return JSONResponse([com_links(p) for p in fatia], headers=headers)


# GET /v1/produtos/{id} — com cache condicional (ETag / If-None-Match)
@app.get("/v1/produtos/{pid}", tags=["produtos"], dependencies=[Depends(autenticar)])
def obter(pid: int, response: Response, if_none_match: Optional[str] = Header(default=None)):
    p = DB.get(pid)
    if p is None:
        raise HTTPException(404, f"produto {pid} não encontrado")
    tag = etag_de(p)
    if if_none_match == tag:
        return Response(status_code=304, headers={"ETag": tag})
    response.headers["ETag"] = tag
    response.headers["Cache-Control"] = "max-age=30"
    return com_links(p)


# POST — cria (NÃO idempotente) -> 201 + Location
@app.post("/v1/produtos", status_code=201, tags=["produtos"], dependencies=[Depends(autenticar)])
def criar(novo: ProdutoIn, response: Response):
    global proximo_id
    if any(p["nome"].lower() == novo.nome.lower() for p in DB.values()):
        raise HTTPException(409, f"já existe produto chamado '{novo.nome}'")
    p = {"id": proximo_id, **novo.model_dump()}
    p["categoria"] = p["categoria"].upper()
    DB[proximo_id] = p
    proximo_id += 1
    response.headers["Location"] = f"/v1/produtos/{p['id']}"
    return com_links(p)


# PUT — substitui por completo (idempotente)
@app.put("/v1/produtos/{pid}", tags=["produtos"], dependencies=[Depends(autenticar)])
def substituir(pid: int, novo: ProdutoIn):
    if pid not in DB:
        raise HTTPException(404, f"produto {pid} não encontrado")
    DB[pid] = {"id": pid, **novo.model_dump(), "categoria": novo.categoria.upper()}
    return com_links(DB[pid])


# PATCH — atualização parcial
@app.patch("/v1/produtos/{pid}", tags=["produtos"], dependencies=[Depends(autenticar)])
def atualizar(pid: int, parcial: ProdutoPatch):
    if pid not in DB:
        raise HTTPException(404, f"produto {pid} não encontrado")
    DB[pid].update(parcial.model_dump(exclude_none=True))
    return com_links(DB[pid])


# DELETE — idempotente; 204 sem corpo
@app.delete("/v1/produtos/{pid}", status_code=204, tags=["produtos"], dependencies=[Depends(autenticar)])
def remover(pid: int):
    if pid not in DB:
        raise HTTPException(404, f"produto {pid} não encontrado")
    del DB[pid]
    return Response(status_code=204)


@app.options("/v1/produtos", tags=["produtos"])
def opcoes():
    return Response(status_code=204, headers={"Allow": "GET, POST, OPTIONS"})
