"""Cliente de mensagens REST: cada texto digitado vira um POST /v1/mensagens."""
import os
import sys

import requests

BASE = os.getenv("API_URL", "http://server:8000")
H = {"X-API-Key": os.getenv("API_KEY", "segredo-sd")}

nome = input("Seu nome: ").strip() or "anonimo"
print(f"Conectado a {BASE}. Digite mensagens (/listar mostra o histórico; /sair ou Ctrl+D encerra).")

while True:
    try:
        texto = input("> ").strip()
    except EOFError:
        break
    if texto == "/sair":
        break
    if not texto:
        continue
    try:
        if texto == "/listar":
            r = requests.get(f"{BASE}/v1/mensagens", headers=H, timeout=5)
            for m in r.json():
                print(f"   #{m['numero']} [{m['hora']}] {m['remetente']}: {m['texto']}")
            continue
        r = requests.post(f"{BASE}/v1/mensagens", headers=H, json={"remetente": nome, "texto": texto}, timeout=5)
        r.raise_for_status()
        print(f"  ✔ {r.status_code} Created — mensagem #{r.json()['numero']} (Location: {r.headers['Location']})")
    except requests.RequestException as e:
        print(f"  ✘ erro: {e}", file=sys.stderr)
