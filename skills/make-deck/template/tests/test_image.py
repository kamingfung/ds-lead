"""Tests for the Image block: a picture, such as a make-chart PNG, in a chart region."""

from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image as PILImage
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.util import Emu

from layouts import LAYOUTS, Region
from render_html import render_html
from render_pptx import EMU_PER_PX, render_pptx
from spec import Bullet, Bullets, Deck, Image, Slide, validate
from theme import HOUSE

SOURCE: str = "Orders warehouse extract, 2025"
ALT: str = "Histogram of order sizes, peaking at 3 items"


def _png(folder: Path, width: int = 400, height: int = 200) -> str:
    path: Path = folder / "chart.png"
    PILImage.new("RGB", (width, height), "white").save(path)
    return str(path)


def _deck(image: Image) -> Deck:
    slide: Slide = Slide(
        "chart_2to1",
        "Most orders hold 3 items",
        lead="Order size, items per order, 2025",
        regions={
            "chart": image,
            "takeaways": Bullets((Bullet("Peak", "3 items"),), heading="Takeaways"),
        },
    )
    return Deck("Orders", "Orders", "2026-11-27", (slide,))


def test_chart_regions_accept_an_image(tmp_path: Path) -> None:
    validate(_deck(Image(_png(tmp_path), ALT, SOURCE)))


@pytest.mark.parametrize("name", ["missing.png", "chart.jpg"])
def test_validate_rejects_a_missing_or_non_png_image(tmp_path: Path, name: str) -> None:
    path: Path = tmp_path / name
    if name.endswith(".jpg"):
        PILImage.new("RGB", (4, 4)).save(path)
    with pytest.raises(ValueError, match="image needs an existing .png file"):
        validate(_deck(Image(str(path), ALT, SOURCE)))


def test_validate_rejects_an_image_without_alt_text(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="image needs alt text"):
        validate(_deck(Image(_png(tmp_path), " ", SOURCE)))


def test_html_embeds_the_png_with_alt_text_and_lists_its_source(tmp_path: Path) -> None:
    html: str = render_html(_deck(Image(_png(tmp_path), ALT, SOURCE)), HOUSE)

    assert '<img src="data:image/png;base64,' in html
    assert f'alt="{ALT}"' in html
    assert f"Source: {SOURCE}" in html


def test_pptx_picture_keeps_its_aspect_ratio_centered_in_the_region(
    tmp_path: Path,
) -> None:
    pptx: bytes = render_pptx(
        _deck(Image(_png(tmp_path, 400, 200), ALT, SOURCE)), HOUSE
    )
    slide: object = Presentation(BytesIO(pptx)).slides[0]
    pictures: list[object] = [
        s for s in slide.shapes if s.shape_type == MSO_SHAPE_TYPE.PICTURE
    ]
    region: Region = LAYOUTS["chart_2to1"]["chart"]
    box: tuple[float, float, float, float] = tuple(
        Emu(v * EMU_PER_PX) for v in (region.x, region.y, region.w, region.h)
    )

    assert len(pictures) == 1
    picture: object = pictures[0]
    assert abs(picture.width / picture.height - 2.0) < 0.01
    assert picture.width <= box[2] + 1 and picture.height <= box[3] + 1
    assert abs((picture.left - box[0]) - (box[2] - picture.width) / 2) <= EMU_PER_PX
    assert abs((picture.top - box[1]) - (box[3] - picture.height) / 2) <= EMU_PER_PX
    assert picture._element.nvPicPr.cNvPr.get("descr") == ALT
