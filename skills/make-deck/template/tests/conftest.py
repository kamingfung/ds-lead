"""Make the template modules importable from the tests folder."""

import sys
from pathlib import Path

TEMPLATE: str = str(Path(__file__).resolve().parents[1])
if TEMPLATE not in sys.path:
    sys.path.insert(0, TEMPLATE)
