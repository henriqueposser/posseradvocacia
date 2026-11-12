#!/usr/bin/env python3
"""Gera a capa de um post do Radar jurídico com o Gemini e salva em radar/img/<slug>.webp.

Uso: python3 _radar/capa.py <slug> "<descrição da cena>" [--saida <arquivo.webp>] [--modelo <id>]

A chave vem de GEMINI_API_KEY (ambiente) ou de `ratoeira-chave GEMINI_API_KEY`.
O estilo fixo (fotografia realista, campo gaúcho, 16:9, sem texto) é acrescentado à descrição.
"""
import base64
import io
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELO = "gemini-3.1-flash-image"
ESTILO = (
    "Fotografia editorial realista, luz natural suave, paleta de verdes, terra e dourado, "
    "ambientada no interior do Rio Grande do Sul quando fizer sentido. Composição horizontal limpa, "
    "com um assunto principal claro. Sem nenhum texto, letra, número, logotipo, marca d'água ou placa legível. "
    "Sem pessoas reconhecíveis em primeiro plano."
)


def chave():
    k = os.environ.get("GEMINI_API_KEY")
    if k:
        return k
    return subprocess.run(["ratoeira-chave", "GEMINI_API_KEY"], capture_output=True, text=True, check=True).stdout.strip()


def gerar(descricao, modelo):
    corpo = {
        "contents": [{"parts": [{"text": f"{descricao}\n\n{ESTILO}"}]}],
        "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9"}},
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
        data=json.dumps(corpo).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": chave()},
    )
    try:
        resp = json.load(urllib.request.urlopen(req, timeout=180))
    except urllib.error.HTTPError as e:
        erro = json.loads(e.read() or b"{}").get("error", {})
        sys.exit(f"O Gemini recusou ({e.code} {erro.get('status', '')}): {erro.get('message', '')[:300]}")
    for parte in resp.get("candidates", [{}])[0].get("content", {}).get("parts", []):
        dado = parte.get("inlineData") or parte.get("inline_data")
        if dado:
            return base64.b64decode(dado["data"])
    sys.exit("O Gemini não devolveu imagem: " + json.dumps(resp)[:300])


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    slug, descricao = sys.argv[1], sys.argv[2]
    modelo = sys.argv[sys.argv.index("--modelo") + 1] if "--modelo" in sys.argv else MODELO
    saida = sys.argv[sys.argv.index("--saida") + 1] if "--saida" in sys.argv else os.path.join(RAIZ, "radar", "img", f"{slug}.webp")
    img = Image.open(io.BytesIO(gerar(descricao, modelo))).convert("RGB")
    if img.width > 1600:
        img = img.resize((1600, round(img.height * 1600 / img.width)), Image.LANCZOS)
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    img.save(saida, "WEBP", quality=82)
    print(f"Capa salva: {saida} ({img.width}x{img.height}, {os.path.getsize(saida) // 1024} KB)")


if __name__ == "__main__":
    main()
