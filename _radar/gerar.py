#!/usr/bin/env python3
"""Gera o blog Radar jurídico a partir de _radar/posts/*.md.

Cada post é um arquivo com cabeçalho entre '---' (uma chave por linha, valor em JSON)
e o corpo em Markdown (HTML também vale). Post com data no futuro não é publicado.

Uso: python3 _radar/gerar.py [--hoje AAAA-MM-DD]
Gera: radar/index.html, radar/<slug>/index.html, radar/feed.xml, sitemap.xml, robots.txt
e atualiza os 3 posts recentes na página inicial (entre os marcadores radar:recentes).
"""
import datetime as dt
import html
import json
import os
import re
import shutil
import sys

import markdown

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(RAIZ, "_radar", "posts")
SAIDA = os.path.join(RAIZ, "radar")
DOMINIO = "https://posseradvocacia.com.br"
WHATS = "https://wa.me/55996745903"
AREAS = ["Ambiental", "Rural e agrário", "Trabalhista", "Cível", "Engenharia florestal"]
MESES = "janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro".split()


def slugify(s):
    tab = str.maketrans("áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ", "aaaaeeiooouc" + "AAAAEEIOOOUC")
    return re.sub(r"[^a-z0-9]+", "-", s.translate(tab).lower()).strip("-")


def data_br(d):
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def e(s):
    return html.escape(s or "", quote=True)


def ler_posts(hoje):
    posts = []
    for f in sorted(os.listdir(POSTS)):
        if not f.endswith(".md"):
            continue
        texto = open(os.path.join(POSTS, f), encoding="utf-8").read()
        _, cab, corpo = texto.split("---\n", 2)
        p = {}
        for linha in cab.strip().splitlines():
            k, v = linha.split(":", 1)
            p[k.strip()] = json.loads(v.strip())
        p["slug"] = f[:-3]
        p["data_obj"] = dt.date.fromisoformat(p["data"])
        if p.get("rascunho") or p["data_obj"] > hoje:
            continue
        if p["area"] not in AREAS:
            sys.exit(f"Área desconhecida em {f}: {p['area']}")
        p["html"] = markdown.markdown(corpo, extensions=["extra", "toc", "sane_lists"])
        posts.append(p)
    posts.sort(key=lambda p: (p["data_obj"], p["titulo"]), reverse=True)
    return posts


def cabecalho(rel, titulo, descricao, url, imagem=None, tipo="website", extra_head=""):
    img = f"{DOMINIO}/radar/img/{imagem}" if imagem else f"{DOMINIO}/imgs/Blog.png"
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(titulo)}</title>
  <meta name="description" content="{e(descricao)}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="{tipo}">
  <meta property="og:title" content="{e(titulo)}">
  <meta property="og:description" content="{e(descricao)}">
  <meta property="og:image" content="{img}">
  <meta property="og:url" content="{url}">
  <meta property="og:site_name" content="Radar jurídico · POSSER Advocacia">
  <meta property="og:locale" content="pt_BR">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="alternate" type="application/rss+xml" title="Radar jurídico" href="{DOMINIO}/radar/feed.xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Darker+Grotesque:wght@300..900&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{rel}styles.css">
  <link rel="stylesheet" href="{rel}radar/radar.css">
  <link rel="icon" type="image/svg+xml" href="{rel}icons/favicon.svg">
{extra_head}</head>

<body class="pagina-radar">
  <header class="site-header" id="siteHeader">
    <div class="wrap header-inner">
      <nav class="main-nav" id="mainNav">
        <a href="{rel}#quem-somos">Quem somos</a>
        <a href="{rel}#areas">Áreas de atuação</a>
        <a href="{rel}radar/">Blog</a>
        <a href="{rel}#contato">Contato</a>
        <a href="{WHATS}" target="_blank" class="nav-cta-mobile">Conversar com especialista</a>
      </nav>
      <a href="{WHATS}" target="_blank" class="btn btn-outline header-cta">
        <span class="cta-label">Conversar com especialista</span>
        <span aria-hidden="true">→</span></a>
      <button class="nav-toggle" id="navToggle" aria-label="Abrir menu" aria-expanded="false">
        <svg class="nav-toggle-icon" viewBox="0 0 34 34" aria-hidden="true" focusable="false">
          <line class="nav-toggle-bar" x1="6" y1="11" x2="28" y2="11"></line>
          <line class="nav-toggle-bar" x1="6" y1="17" x2="28" y2="17"></line>
          <line class="nav-toggle-bar" x1="6" y1="23" x2="28" y2="23"></line>
        </svg>
      </button>
    </div>
  </header>
"""


def rodape(rel):
    logo = re.search(r'<div class="footer-logo">.*?</div>', open(os.path.join(RAIZ, "index.html"), encoding="utf-8").read(), re.S).group(0)
    return f"""
  <footer class="site-footer">
    <div class="wrap footer-inner">
      <div class="footer-contact">
        <p>Santa Maria, Rio Grande do Sul</p>
        <p>Rua Paul Harris, 91, sala 16</p>
        <p>Rio Grande do Sul</p>
        <p><a href="tel:+5555996745903">+55 (55) 99674-5903</a></p>
        <a href="{WHATS}" target="_blank" class="btn btn-outline footer-cta">
          Conversar com especialista
          <span aria-hidden="true">→</span>
        </a>
      </div>
      <nav class="footer-nav">
        <a href="{rel}#quem-somos">Quem somos</a>
        <a href="{rel}#areas">Áreas de atuação</a>
        <a href="{rel}radar/">Blog</a>
        <a href="{rel}#contato">Contato</a>
      </nav>
      {logo}
    </div>
    <div class="wrap footer-bottom">
      <div class="footer-socials">
        <a href="https://www.instagram.com/henriqueposseradv/" aria-label="Instagram" target="_blank">
          <img src="{rel}icons/instagram.svg" alt="Instagram">
        </a>
        <a href="{WHATS}" aria-label="WhatsApp" target="_blank">
          <img src="{rel}icons/whatsapp.svg" alt="WhatsApp">
        </a>
      </div>
      <p class="footer-copy">© {dt.date.today().year} POSSER Advocacia. Todos os direitos reservados.</p>
    </div>
  </footer>
  <script src="{rel}script.js"></script>
</body>
</html>
"""


def card(p, rel_img, rel_post):
    capa = f'<img src="{rel_img}{e(p["capa"])}" alt="" loading="lazy">' if p.get("capa") else ""
    return f"""      <a class="post-card" href="{rel_post}{p['slug']}/" data-area="{slugify(p['area'])}">
        <div class="post-card-capa">{capa}</div>
        <div class="post-card-texto">
          <p class="post-card-meta"><span class="selo selo--{slugify(p['area'])}">{e(p['area'])}</span> <time datetime="{p['data']}">{data_br(p['data_obj'])}</time></p>
          <h3>{e(p['titulo'])}</h3>
          <p class="post-card-resumo">{e(p['resumo'])}</p>
        </div>
      </a>
"""


def pagina_indice(posts):
    rel = "../"
    filtros = '<button class="filtro is-ativo" data-filtro="todas">Todas</button>' + "".join(
        f'<button class="filtro" data-filtro="{slugify(a)}">{e(a)}</button>' for a in AREAS if any(p["area"] == a for p in posts))
    cards = "".join(card(p, "img/", "") for p in posts)
    h = cabecalho(rel, "Radar jurídico · POSSER Advocacia",
                  "Análises e orientações para tomar decisões jurídicas inteligentes no seu cotidiano. Direito ambiental, rural, trabalhista e cível.",
                  f"{DOMINIO}/radar/")
    h += f"""
  <section class="hero radar-hero">
    <div class="hero-media"><img src="{rel}imgs/Banner 2.jpg" alt=""></div>
    <div class="radar-hero-scrim"></div>
    <div class="wrap radar-hero-content">
      <p class="radar-eyebrow">Blog</p>
      <h1>Radar jurídico</h1>
      <p class="radar-hero-lead">Análises e orientações para tomar decisões jurídicas inteligentes no seu cotidiano.</p>
    </div>
  </section>

  <main class="radar-main">
    <div class="wrap">
      <div class="filtros" role="group" aria-label="Filtrar por área">{filtros}</div>
      <div class="post-grid" id="postGrid">
{cards}      </div>
    </div>
  </main>
  <script>
    document.querySelectorAll('.filtro').forEach(b => b.addEventListener('click', () => {{
      document.querySelectorAll('.filtro').forEach(x => x.classList.toggle('is-ativo', x === b));
      const f = b.dataset.filtro;
      document.querySelectorAll('.post-card').forEach(c => c.hidden = f !== 'todas' && c.dataset.area !== f);
    }}));
  </script>
"""
    h += rodape(rel)
    return h


def pagina_post(p, posts):
    rel = "../../"
    url = f"{DOMINIO}/radar/{p['slug']}/"
    relacionados = [q for q in posts if q["area"] == p["area"] and q is not p][:3]
    if len(relacionados) < 3:
        relacionados += [q for q in posts if q is not p and q not in relacionados][: 3 - len(relacionados)]
    ld = {
        "@context": "https://schema.org", "@type": "BlogPosting", "headline": p["titulo"],
        "description": p["resumo"], "datePublished": p["data"], "dateModified": p.get("atualizado") or p["data"],
        "image": f"{DOMINIO}/radar/img/{p['capa']}" if p.get("capa") else None, "mainEntityOfPage": url,
        "author": {"@type": "Person", "name": "Henrique Posser Martins", "url": DOMINIO + "/"},
        "publisher": {"@type": "LegalService", "name": "POSSER Advocacia", "url": DOMINIO + "/"},
    }
    extra = f'  <meta property="article:published_time" content="{p["data"]}">\n  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n'
    h = cabecalho(rel, f"{p['titulo']} · Radar jurídico", p["resumo"], url, p.get("capa"), "article", extra)
    capa = f'<figure class="artigo-capa"><img src="../img/{e(p["capa"])}" alt=""></figure>' if p.get("capa") else ""
    h += f"""
  <section class="hero radar-hero radar-hero--post">
    <div class="hero-media"><img src="{rel}imgs/Banner 2.jpg" alt=""></div>
    <div class="radar-hero-scrim"></div>
    <div class="wrap radar-hero-content">
      <p class="radar-eyebrow"><a href="../">Radar jurídico</a> · {e(p['area'])}</p>
      <h1>{e(p['titulo'])}</h1>
      <p class="radar-hero-meta">Henrique Posser · OAB/RS 117.583 · <time datetime="{p['data']}">{data_br(p['data_obj'])}</time></p>
    </div>
  </section>

  <main class="radar-main">
    <article class="artigo">
      {capa}
      <div class="artigo-corpo">
{p['html']}
      </div>
      <aside class="artigo-cta">
        <h2>Precisa de orientação nesse tema?</h2>
        <p>Cada caso tem detalhes que mudam a resposta. Converse comigo e entenda o caminho mais seguro para a sua situação.</p>
        <a href="{WHATS}" target="_blank" class="btn btn-outline-dark">Conversar com especialista <span aria-hidden="true">→</span></a>
      </aside>
    </article>
    <section class="wrap relacionados">
      <h2>Leia também</h2>
      <div class="post-grid">
{''.join(card(q, '../img/', '../') for q in relacionados)}      </div>
    </section>
  </main>
"""
    h += rodape(rel)
    return h


def feed(posts):
    itens = "".join(f"""  <item>
    <title>{e(p['titulo'])}</title>
    <link>{DOMINIO}/radar/{p['slug']}/</link>
    <guid>{DOMINIO}/radar/{p['slug']}/</guid>
    <pubDate>{dt.datetime.combine(p['data_obj'], dt.time(9)).strftime('%a, %d %b %Y %H:%M:%S -0300')}</pubDate>
    <category>{e(p['area'])}</category>
    <description>{e(p['resumo'])}</description>
  </item>
""" for p in posts[:30])
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Radar jurídico · POSSER Advocacia</title>
  <link>{DOMINIO}/radar/</link>
  <description>Análises e orientações para tomar decisões jurídicas inteligentes no seu cotidiano.</description>
  <language>pt-br</language>
{itens}</channel>
</rss>
"""


def sitemap(posts):
    urls = [(f"{DOMINIO}/", None), (f"{DOMINIO}/radar/", posts[0]["data"] if posts else None)]
    urls += [(f"{DOMINIO}/radar/{p['slug']}/", p.get("atualizado") or p["data"]) for p in posts]
    corpo = "".join(f"  <url><loc>{u}</loc>{f'<lastmod>{d}</lastmod>' if d else ''}</url>\n" for u, d in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{corpo}</urlset>\n'


def atualizar_inicio(posts):
    caminho = os.path.join(RAIZ, "index.html")
    h = open(caminho, encoding="utf-8").read()
    bloco = "<!-- radar:recentes -->\n" + "".join(card(p, "radar/img/", "radar/") for p in posts[:3]) + "      <!-- /radar:recentes -->"
    novo = re.sub(r"<!-- radar:recentes -->.*?<!-- /radar:recentes -->", lambda m: bloco, h, flags=re.S)
    if novo != h:
        open(caminho, "w", encoding="utf-8").write(novo)


def escrever(caminho, texto):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    open(caminho, "w", encoding="utf-8").write(texto)


def main():
    hoje = dt.date.today()
    if "--hoje" in sys.argv:
        hoje = dt.date.fromisoformat(sys.argv[sys.argv.index("--hoje") + 1])
    posts = ler_posts(hoje)
    # apaga páginas de posts antigas (pasta com index.html gerado), preserva img/ e radar.css
    for nome in os.listdir(SAIDA):
        alvo = os.path.join(SAIDA, nome)
        if os.path.isdir(alvo) and nome != "img":
            shutil.rmtree(alvo)
    escrever(os.path.join(SAIDA, "index.html"), pagina_indice(posts))
    for p in posts:
        escrever(os.path.join(SAIDA, p["slug"], "index.html"), pagina_post(p, posts))
    escrever(os.path.join(SAIDA, "feed.xml"), feed(posts))
    escrever(os.path.join(RAIZ, "sitemap.xml"), sitemap(posts))
    escrever(os.path.join(RAIZ, "robots.txt"), f"User-agent: *\nAllow: /\nSitemap: {DOMINIO}/sitemap.xml\n")
    atualizar_inicio(posts)
    print(f"{len(posts)} posts publicados (data de corte {hoje.isoformat()})")


if __name__ == "__main__":
    main()
