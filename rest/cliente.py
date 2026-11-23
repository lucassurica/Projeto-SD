import requests

BASE = "http://localhost:5000"

AJUDA = """Digite uma mensagem e tecle ENTER para enviar ao servidor (POST).
Comandos:
  /listar              lista todas as mensagens        (GET /mensagens)
  /ver ID              mostra uma mensagem             (GET /mensagens/ID)
  /editar ID TEXTO     altera o texto de uma mensagem  (PUT /mensagens/ID)
  /apagar ID           remove uma mensagem             (DELETE /mensagens/ID)
  /ajuda               mostra esta ajuda
  /sair                encerra (ou Ctrl+D)"""


def mostrar(titulo, r):
    print(f"  {titulo:<22} -> {r.status_code} {r.text.strip()}")


def main():
    remetente = input("Seu nome: ").strip() or "anonimo"
    print(f"\nConectado a {BASE}.\n{AJUDA}\n")

    while True:
        try:
            entrada = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not entrada:
            continue

        try:
            if not entrada.startswith("/"):
                mostrar("POST /mensagens", requests.post(f"{BASE}/mensagens", json={"remetente": remetente, "texto": entrada}))
                continue

            cmd, _, resto = entrada.partition(" ")
            if cmd == "/sair":
                break
            elif cmd == "/ajuda":
                print(AJUDA)
            elif cmd == "/listar":
                mostrar("GET /mensagens", requests.get(f"{BASE}/mensagens"))
            elif cmd == "/ver" and resto.strip().isdigit():
                mostrar(f"GET /mensagens/{resto.strip()}", requests.get(f"{BASE}/mensagens/{resto.strip()}"))
            elif cmd == "/editar" and resto.split(" ", 1)[0].isdigit() and " " in resto:
                mid, texto = resto.split(" ", 1)
                mostrar(f"PUT /mensagens/{mid}", requests.put(f"{BASE}/mensagens/{mid}", json={"texto": texto}))
            elif cmd == "/apagar" and resto.strip().isdigit():
                mostrar(f"DELETE /mensagens/{resto.strip()}", requests.delete(f"{BASE}/mensagens/{resto.strip()}"))
            else:
                print("  comando invalido. Digite /ajuda")
        except requests.ConnectionError:
            print(f"  nao consegui conectar em {BASE}. O servidor esta rodando? (python servidor.py)")


if __name__ == "__main__":
    main()
