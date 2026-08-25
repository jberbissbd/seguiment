"""Hooks de MkDocs per a aquest repositori.

Actualment només reutilitza el README.md de l'arrel com a contingut de la
pàgina d'inici del lloc de documentació, per no mantenir dues còpies del
mateix text.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]
README_PATH = REPO_ROOT / "README.md"

# El README.md enllaça les guies com "docs/ENGINEERING.md" (relatiu a
# l'arrel del repositori, tal com ho interpreta GitHub). Un cop el mateix
# text es publica com a docs/index.md, aquests enllaços s'han de resoldre
# relatius a `docs/`, així que cal treure el prefix `docs/`.
_DOCS_LINK = re.compile(r"\]\(docs/")


def on_page_markdown(markdown, *, page, config, files):
    """Substitueix el contingut de la pàgina d'inici pel README.md del repositori.

    Args:
        markdown: Contingut Markdown original de la pàgina (ignorat per a
            `index.md`; `docs/index.md` només existeix com a punt d'entrada
            de la navegació).
        page: Pàgina que s'està processant.
        config: Configuració activa de MkDocs (no s'utilitza).
        files: Col·lecció de fitxers del lloc (no s'utilitza).

    Returns:
        El Markdown a renderitzar per a aquesta pàgina.
    """
    if page.file.src_uri != "index.md":
        return markdown
    readme = README_PATH.read_text(encoding="utf-8")
    return _DOCS_LINK.sub("](", readme)
