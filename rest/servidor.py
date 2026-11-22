from flask import Flask, jsonify, request

app = Flask(__name__)
mensagens = {}      # id -> {"id", "remetente", "texto"}
proximo_id = 1


@app.post("/mensagens")                      # CREATE
def criar():
    global proximo_id
    dados = request.get_json(silent=True) or {}
    if "texto" not in dados:
        return jsonify(erro="campo 'texto' obrigatorio"), 400
    msg = {"id": proximo_id, "remetente": dados.get("remetente", "anonimo"), "texto": dados["texto"]}
    mensagens[proximo_id] = msg
    proximo_id += 1
    print("[POST]", msg, flush=True)
    resp = jsonify(msg)
    resp.status_code = 201
    resp.headers["Location"] = f"/mensagens/{msg['id']}"
    return resp


@app.get("/mensagens")                       # READ (lista)
def listar():
    return jsonify(list(mensagens.values()))


@app.get("/mensagens/<int:mid>")             # READ (um)
def obter(mid):
    if mid not in mensagens:
        return jsonify(erro="nao encontrada"), 404
    return jsonify(mensagens[mid])


@app.put("/mensagens/<int:mid>")             # UPDATE
def atualizar(mid):
    if mid not in mensagens:
        return jsonify(erro="nao encontrada"), 404
    mensagens[mid]["texto"] = (request.get_json() or {}).get("texto", mensagens[mid]["texto"])
    return jsonify(mensagens[mid])


@app.delete("/mensagens/<int:mid>")          # DELETE
def remover(mid):
    if mensagens.pop(mid, None) is None:
        return jsonify(erro="nao encontrada"), 404
    return "", 204


if __name__ == "__main__":
    app.run(port=5000)
