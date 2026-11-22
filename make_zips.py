#!/usr/bin/env python3
"""Gera dist/<protocolo>.zip com o código-fonte de cada pasta (sem lixo de build)."""
import pathlib
import zipfile

RAIZ = pathlib.Path(__file__).parent
IGNORAR = {"__pycache__", "node_modules", ".git"}
(RAIZ / "dist").mkdir(exist_ok=True)

for proto in ("grpc", "rest", "rabbitmq", "kafka"):
    destino = RAIZ / "dist" / f"{proto}.zip"
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted((RAIZ / proto).rglob("*")):
            if f.is_file() and not (set(f.parts) & IGNORAR) and f.suffix != ".pyc":
                z.write(f, f.relative_to(RAIZ))
    print(f"{destino.relative_to(RAIZ)}  ({destino.stat().st_size // 1024} KB, {len(zipfile.ZipFile(destino).namelist())} arquivos)")
