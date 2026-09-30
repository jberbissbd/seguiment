"""Copia o empaqueta l'artefacte de build generat a la carpeta `release/`.

Els binaris Windows es copien tal qual. Els binaris Unix (Linux i macOS) es
comprimeixen en un `.tar.gz`, ja que GitHub Releases no conserva el bit
d'execució en fitxers solts: sense això, calia executar `chmod +x` manualment
després de cada descàrrega.
"""

import os
import shutil
import stat
import tarfile
from pathlib import Path


source = Path(os.environ["SOURCE_FILE"])
output_name = os.environ["OUTPUT_FILE"]
destination = Path("release") / output_name
if not source.is_file():
    raise SystemExit(f"No s'ha generat l'artefacte esperat: {source}")
destination.parent.mkdir(parents=True, exist_ok=True)

if output_name.endswith(".tar.gz"):
    source.chmod(source.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    with tarfile.open(destination, "w:gz") as archive:
        archive.add(source, arcname="Tutopy")
else:
    shutil.copy2(source, destination)
