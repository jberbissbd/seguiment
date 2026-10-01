"""Comprovació de versió nova disponible a GitHub Releases."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass

from tutopy import __version__

LOGGER = logging.getLogger(__name__)

RELEASES_API_URL = "https://api.github.com/repos/jberbissbd/seguiment/releases/latest"
REQUEST_TIMEOUT_SECONDS = 5.0


@dataclass(frozen=True)
class UpdateCheckResult:
    """Resultat d'una comprovació de versió.

    Attributes:
        update_available: Si hi ha una versió més nova publicada.
        latest_version: Etiqueta de la versió més recent (p. ex. "1.4.0"),
            o `None` si no s'ha pogut determinar.
        release_url: URL de la pàgina de la release a GitHub, o `None`.
    """

    update_available: bool
    latest_version: str | None
    release_url: str | None


class UpdateCheckService:
    """Consulta l'API pública de GitHub Releases i la compara amb la versió local.

    No fa cap crida amb autenticació ni envia cap dada de l'usuari: és una
    petició GET anònima a un punt final públic. Qualsevol error de xarxa,
    de temps d'espera o de resposta inesperada es registra i es tradueix en
    un resultat "sense actualització", mai en una excepció que pugui
    interrompre l'arrencada de l'aplicació.
    """

    def __init__(
        self,
        current_version: str = __version__,
        releases_url: str = RELEASES_API_URL,
        timeout: float = REQUEST_TIMEOUT_SECONDS,
    ):
        """Rep la versió local a comparar i, opcionalment, l'URL i el timeout."""
        self.current_version = current_version
        self.releases_url = releases_url
        self.timeout = timeout

    def check_for_update(self) -> UpdateCheckResult:
        """Comprova si hi ha una versió més nova publicada.

        Síncrona i bloquejant: qui la crida l'ha d'executar en un fil
        secundari (p. ex. amb `BackgroundTaskRunner`).
        """
        try:
            request = urllib.request.Request(
                self.releases_url,
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "Tutopy",
                },
            )
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read())
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as error:
            LOGGER.info("No s'ha pogut comprovar si hi ha una versió nova: %s", error)
            return UpdateCheckResult(False, None, None)

        tag_name = payload.get("tag_name") or ""
        latest_version = tag_name.lstrip("v") or None
        release_url = payload.get("html_url")
        update_available = bool(
            latest_version and _is_newer(latest_version, self.current_version)
        )
        return UpdateCheckResult(update_available, latest_version, release_url)


def _is_newer(remote: str, local: str) -> bool:
    """Compara dues versions `MAJOR.MINOR.PATCH` sense dependències externes."""

    def parts(value: str) -> tuple[int, ...] | None:
        fragments = value.split(".")
        if not all(fragment.isdigit() for fragment in fragments):
            return None
        return tuple(int(fragment) for fragment in fragments)

    remote_parts = parts(remote)
    local_parts = parts(local)
    if remote_parts is None or local_parts is None:
        return False
    return remote_parts > local_parts
