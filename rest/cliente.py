import requests

BASE = "http://localhost:5000"


def mostrar(titulo, r):
    print(f"{titulo:<22} -> {r.status_code} {r.text.strip()}")


mostrar("POST /mensagens", requests.post(f"{BASE}/mensagens", json={"remetente": "cliente", "texto": "Ola, servidor!"}))
mostrar("POST invalido", requests.post(f"{BASE}/mensagens", json={}))
mostrar("GET /mensagens", requests.get(f"{BASE}/mensagens"))
mostrar("GET /mensagens/1", requests.get(f"{BASE}/mensagens/1"))
mostrar("PUT /mensagens/1", requests.put(f"{BASE}/mensagens/1", json={"texto": "Texto editado"}))
mostrar("DELETE /mensagens/1", requests.delete(f"{BASE}/mensagens/1"))
mostrar("GET /mensagens/1", requests.get(f"{BASE}/mensagens/1"))
