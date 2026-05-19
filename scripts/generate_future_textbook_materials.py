from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.generate_real_lesson_materials import main  # noqa: E402


if __name__ == "__main__":
    print(
        "generate_future_textbook_materials.py is kept for compatibility. "
        "Generating the real-data lesson materials instead."
    )
    main()
