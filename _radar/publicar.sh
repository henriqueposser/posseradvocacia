#!/usr/bin/env bash
# Publica no blog os posts cuja data chegou: gera as páginas e, se algo mudou, envia pro GitHub Pages.
# Roda todo dia pela automação "Radar jurídico · publicar" da Ratoeira.
set -euo pipefail

SITE="$(cd "$(dirname "$0")/.." && pwd)"
G=(git --git-dir="$HOME/servicos/site-posseradvocacia.git" --work-tree="$SITE")
REPO="https://github.com/henriqueposser/posseradvocacia.git"

python3 "$SITE/_radar/gerar.py"

"${G[@]}" add -A
if "${G[@]}" diff --cached --quiet; then
  echo "Nada novo pra publicar hoje."
  exit 0
fi

novos=$("${G[@]}" diff --cached --name-only --diff-filter=A -- 'radar/*/index.html' | sed -E 's#radar/(.*)/index.html#\1#' | paste -sd ', ' -)
"${G[@]}" commit -qm "Radar jurídico: publica ${novos:-atualizações} ($(date +%F))"

TOKEN="$(ratoeira-chave GITHUB_TOKEN)"
B=$(printf 'x-access-token:%s' "$TOKEN" | base64 -w0)
"${G[@]}" -c http.extraHeader="Authorization: Basic $B" push -q "$REPO" main
echo "Publicado: ${novos:-páginas atualizadas}"
