"""pytest configuration for the renderer contract/integrity tests.

The renderer lives in ``report-renderer/`` as a flat module directory
(``render_report.py``, ``contract.py``, ``visual_qa.py``), not as a package.
This conftest puts that directory on ``sys.path`` so the tests can import
``contract`` and ``visual_qa`` directly.
"""

import sys
from pathlib import Path

RENDERER_DIR = Path(__file__).resolve().parents[1]
if str(RENDERER_DIR) not in sys.path:
    sys.path.insert(0, str(RENDERER_DIR))