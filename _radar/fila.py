#!/usr/bin/env python3
"""Mostra a fila do Radar jurídico: o que sai hoje, os rascunhos aguardando aprovação e os próximos.

Uso: python3 _radar/fila.py [--hoje AAAA-MM-DD] [--json]
"""
import datetime as dt
import json
import os
import sys

POSTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posts")


def ler():
    for f in sorted(os.listdir(POSTS)):
        if not f.endswith(".md"):
            continue
        cab = open(os.path.join(POSTS, f), encoding="utf-8").read().split("---\n", 2)[1]
        p = {k.strip(): json.loads(v.strip()) for k, v in (l.split(":", 1) for l in cab.strip().splitlines())}
        p["slug"] = f[:-3]
        yield p


def main():
    hoje = dt.date.today()
    if "--hoje" in sys.argv:
        hoje = dt.date.fromisoformat(sys.argv[sys.argv.index("--hoje") + 1])
    posts = list(ler())
    fila = sorted((p for p in posts if not p.get("rascunho") and p["data"] > hoje.isoformat()), key=lambda p: p["data"])
    r = {
        "hoje": [p for p in posts if not p.get("rascunho") and p["data"] == hoje.isoformat()],
        "rascunhos": sorted((p for p in posts if p.get("rascunho")), key=lambda p: p["data"]),
        "proximos": fila[:3],
        "na_fila": len(fila),
        "ultimo_agendado": fila[-1]["data"] if fila else None,
    }
    if "--json" in sys.argv:
        print(json.dumps({k: ([{c: p[c] for c in ("titulo", "data", "area", "slug")} for p in v] if isinstance(v, list) else v)
                          for k, v in r.items()}, ensure_ascii=False, indent=1))
        return
    for nome, chave in (("Sai hoje", "hoje"), ("Aguardando aprovação", "rascunhos"), ("Próximos", "proximos")):
        print(f"{nome}:")
        for p in r[chave]:
            print(f"  {p['data']}  {p['titulo']}  (/radar/{p['slug']}/)")
        if not r[chave]:
            print("  nada")
    print(f"Na fila: {r['na_fila']} posts, até {r['ultimo_agendado'] or '-'}")


if __name__ == "__main__":
    main()
