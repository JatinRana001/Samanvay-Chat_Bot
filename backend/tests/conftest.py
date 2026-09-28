import sys
import os
from pathlib import Path

backend_root = str(Path(__file__).parent.parent.resolve())
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)
