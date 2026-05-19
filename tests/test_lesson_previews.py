from pathlib import Path

import matplotlib.pyplot as plt
import pytest

from quant_trading.lesson_previews import plot_future_lesson_preview


def test_future_lesson_previews_generate_images(tmp_path: Path) -> None:
    for chapter in range(11, 31):
        output_path = tmp_path / f"{chapter}.png"

        figure = plot_future_lesson_preview(chapter, output_path)
        plt.close(figure)

        assert output_path.exists()
        assert output_path.stat().st_size > 0


def test_future_lesson_preview_rejects_unknown_chapter(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unknown future lesson chapter"):
        plot_future_lesson_preview(99, tmp_path / "missing.png")
