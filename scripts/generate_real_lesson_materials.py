from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_trading.real_lessons import LESSON_SPECS, run_all_real_lessons  # noqa: E402


def main() -> None:
    write_lesson_scripts()
    write_lesson_notebooks()
    results = run_all_real_lessons(PROJECT_ROOT)
    for result in results:
        print(f"generated {result.spec.chapter:02d}: {result.spec.title}")
        print(f"  report: {result.report_path}")
        print(f"  textbook: {result.textbook_path}")


def write_lesson_scripts() -> None:
    scripts_dir = PROJECT_ROOT / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    for spec in LESSON_SPECS.values():
        path = scripts_dir / spec.script_file
        path.write_text(_render_lesson_script(spec.chapter), encoding="utf-8")


def write_lesson_notebooks() -> None:
    notebooks_dir = PROJECT_ROOT / "notebooks"
    notebooks_dir.mkdir(parents=True, exist_ok=True)
    for spec in LESSON_SPECS.values():
        path = notebooks_dir / spec.notebook_file
        notebook = _render_notebook(spec.chapter, spec.title)
        path.write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")


def _render_lesson_script(chapter: int) -> str:
    return f'''from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from quant_trading.real_lessons import run_chapter_cli  # noqa: E402


if __name__ == "__main__":
    run_chapter_cli({chapter}, PROJECT_ROOT)
'''


def _render_notebook(chapter: int, title: str) -> dict[str, object]:
    source_markdown = [
        f"# {chapter:02d} {title}\\n",
        "\\n",
        "这个 notebook 会运行本章真实数据实验，并同步生成报告、课本图示和结果表。\\n",
    ]
    source_code = [
        "import sys\\n",
        "from pathlib import Path\\n",
        "\\n",
        "PROJECT_ROOT = Path.cwd().resolve()\\n",
        "if not (PROJECT_ROOT / 'src').exists():\\n",
        "    PROJECT_ROOT = PROJECT_ROOT.parent\\n",
        "SRC_PATH = PROJECT_ROOT / 'src'\\n",
        "if str(SRC_PATH) not in sys.path:\\n",
        "    sys.path.insert(0, str(SRC_PATH))\\n",
        "\\n",
        "from IPython.display import Image, display\\n",
        "from quant_trading.real_lessons import run_chapter_cli\\n",
        "\\n",
        f"result = run_chapter_cli({chapter}, PROJECT_ROOT)\\n",
        "display(result.summary)\\n",
        "display(Image(filename=str(result.image_path)))\\n",
    ]
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": source_markdown,
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": source_code,
            },
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


if __name__ == "__main__":
    main()
