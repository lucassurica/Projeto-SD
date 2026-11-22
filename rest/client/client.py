"""Cliente REST em Python (requests) — percorre as características do REST."""
import os
import time

import requests

BASE = os.getenv("API_URL", "http://server:8000")
H = {"X-API-Key": os.getenv("API_KEY", "segredo-sd")}


def titulo(t):
    print(f"\n=== {t} ===")


def mostra(r, corpo=True):
    print(f"{r.request.method} {r.request.path_url}  ->  {r.status_code} {r.reason}")
    for h in ("Location", "ETag", "Cache-Control", "Link", "X-Total-Count", "Content-Type"):
        if h in r.headers:
            print(f"   {h}: {r.headers[h]}")
    if corpo and r.content:
        print("  ", r.text[:300])


for _ in range(30):  # espera o servidor subir
    try:
        requests.get(f"{BASE}/saude", timeout=1); break
    except requests.RequestException:
        time.sleep(0.5)

titulo("GET coleção (filtro + paginação via Link header)")
r = requests.get(f"{BASE}/v1/produtos", params={"categoria": "eletronicos", "limite": 1}, headers=H)
mostra(r)

titulo("GET coleção negociando conteúdo: Accept: text/csv")
mostra(requests.get(f"{BASE}/v1/produtos", params={"limite": 3}, headers={**H, "Accept": "text/csv"}))

titulo("POST cria recurso -> 201 Created + Location")
r = requests.post(f"{BASE}/v1/produtos", headers=H,
                  json={"nome": "Mouse Gamer", "categoria": "eletronicos", "preco": 180, "estoque": 25})
mostra(r)
novo = r.headers["Location"]

titulo("POST duplicado -> 409 Conflict")
mostra(requests.post(f"{BASE}/v1/produtos", headers=H,
                     json={"nome": "Mouse Gamer", "categoria": "eletronicos", "preco": 180}))

titulo("POST inválido (preço negativo) -> 422 Unprocessable")
r = requests.post(f"{BASE}/v1/produtos", headers=H, json={"nome": "X", "categoria": "Y", "preco": -5})
mostra(r, corpo=False)

titulo("GET recurso + ETag, depois requisição condicional -> 304")
r = requests.get(f"{BASE}{novo}", headers=H)
mostra(r)
r2 = requests.get(f"{BASE}{novo}", headers={**H, "If-None-Match": r.headers["ETag"]})
mostra(r2)

titulo("PUT (substitui; idempotente: 2x = mesmo resultado)")
corpo = {"nome": "Mouse Gamer Pro", "categoria": "eletronicos", "preco": 220, "estoque": 25}
mostra(requests.put(f"{BASE}{novo}", headers=H, json=corpo), corpo=False)
mostra(requests.put(f"{BASE}{novo}", headers=H, json=corpo), corpo=False)

titulo("PATCH (atualização parcial: só o estoque)")
mostra(requests.patch(f"{BASE}{novo}", headers=H, json={"estoque": 3}))

titulo("DELETE -> 204 No Content; repetir -> 404")
mostra(requests.delete(f"{BASE}{novo}", headers=H))
mostra(requests.delete(f"{BASE}{novo}", headers=H))

titulo("Sem credencial -> 401 Unauthorized (API stateless)")
mostra(requests.get(f"{BASE}/v1/produtos"))

titulo("Documentação OpenAPI gerada automaticamente")
spec = requests.get(f"{BASE}/openapi.json").json()
for caminho, ops in spec["paths"].items():
    print(f"  {caminho}: {', '.join(m.upper() for m in ops)}")
print("  (Swagger UI interativa em http://localhost:8000/docs)")
