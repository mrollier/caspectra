"""Make the repository root importable so ``import caspectra`` works without
an editable install during early development."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.resolve()))
