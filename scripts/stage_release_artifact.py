import os
import shutil
from pathlib import Path


source = Path(os.environ["SOURCE_FILE"])
destination = Path("release") / os.environ["OUTPUT_FILE"]
if not source.is_file():
    raise SystemExit(f"No s'ha generat l'artefacte esperat: {source}")
destination.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(source, destination)
