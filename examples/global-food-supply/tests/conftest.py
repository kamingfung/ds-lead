"""Put the example folder and the make-deck kit on sys.path before the tests import them."""

import sys
from pathlib import Path

EXAMPLE_DIR: Path = Path(__file__).resolve().parents[1]
KIT_DIR: Path = EXAMPLE_DIR.parents[1] / "skills" / "make-deck" / "template"
sys.path[:0] = [str(EXAMPLE_DIR), str(KIT_DIR)]
